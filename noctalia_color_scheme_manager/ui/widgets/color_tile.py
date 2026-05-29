"""Color widgets: swatch, tile, and contrast components."""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, Protocol

import gi  # noqa: E401

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Gdk  # noqa: E402

if TYPE_CHECKING:
    from .preview import ReactiveColors


def hex_to_rgba(color: str) -> Gdk.RGBA:
    """Parse hex color to GdkRGBA."""
    rgba = Gdk.RGBA()
    rgba.parse(color)
    return rgba


def hex_to_rgb(color: str) -> tuple[float, float, float]:
    """Parse hex color to RGB tuple (0.0-1.0 range).

    Supports both 6-digit (#rrggbb) and 3-digit (#rgb) shorthand.
    """
    if not color or len(color) < 4:
        return (0.5, 0.5, 0.5)
    if color.startswith("#") and len(color) == 7:
        r = int(color[1:3], 16) / 255
        g = int(color[3:5], 16) / 255
        b = int(color[5:7], 16) / 255
        return (r, g, b)
    elif color.startswith("#") and len(color) == 4:
        # 3-digit shorthand: #rgb -> #rrggbb
        r = int(color[1] * 2, 16) / 255
        g = int(color[2] * 2, 16) / 255
        b = int(color[3] * 2, 16) / 255
        return (r, g, b)
    return (0.5, 0.5, 0.5)


def darken_color(hex_color: str, amount: float = 0.1) -> str:
    """Darken a hex color by amount (0.0-1.0 range).

    Args:
        hex_color: Hex color string (e.g. "#ff0000")
        amount: Darkening amount (0.0 = no change, 1.0 = full black)

    Returns:
        Darkened hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    r = max(0.0, r - amount)
    g = max(0.0, g - amount)
    b = max(0.0, b - amount)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def validate_hex(hex_color: str) -> bool:
    """Validate a hex color string.

    Args:
        hex_color: Color string to validate

    Returns:
        True if valid 6-digit hex color (e.g. "#ff0000")
    """
    return bool(re.match(r"^#[0-9a-fA-F]{6}$", hex_color))


class ColorSwatch(Gtk.DrawingArea):
    """Colored square swatch drawn on a DrawingArea.

    Args:
        color: Hex color string (e.g. "#ff0000")
        size: Width/height in pixels (default 28)
    """

    def __init__(self, color: str = "#000000", size: int = 28, **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self.set_size_request(size, size)
        self.set_draw_func(self._draw, color)

    def set_color(self, color: str) -> None:
        """Update the swatch color."""
        self._color = color
        self.set_draw_func(self._draw, color)
        self.queue_draw()

    @staticmethod
    def _draw(area, cr, w, h, color):
        r, g, b = hex_to_rgb(color)
        cr.set_source_rgb(r, g, b)
        cr.paint()


class ColorTile(Gtk.Box):
    """Single color row: label + hex entry + color picker.

    Emits color changes through reactive_colors when the user edits
    the hex entry or uses the color picker.

    Args:
        label: Display label for the color row
        color_key: Key in the colors dict (e.g. "mPrimary")
        reactive_colors: ReactiveColors instance to emit changes to
        show_label: Whether to show the label (default True)
    """

    def __init__(  # noqa: PLR0913
        self,
        label: str,
        color_key: str,
        reactive_colors: ReactiveColors | None = None,
        show_label: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.color_key = color_key
        self.reactive_colors = reactive_colors

        self.set_spacing(8)
        self.set_valign(Gtk.Align.CENTER)

        if show_label:
            lbl = Gtk.Label()
            lbl.set_text(label)
            lbl.set_hexpand(False)
            lbl.set_width_chars(14)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_xalign(0)  # Left align text
            self.append(lbl)

        self.hex_entry = Gtk.Entry()
        self.hex_entry.set_text(reactive_colors.get(color_key) if reactive_colors else "#000000")
        self.hex_entry.set_width_chars(8)
        self.hex_entry.set_hexpand(False)
        self.hex_entry.connect("changed", self._on_hex_changed)
        self.append(self.hex_entry)

        self.color_btn = Gtk.ColorButton()
        initial_color = reactive_colors.get(color_key) if reactive_colors else "#000000"
        self.color_btn.set_rgba(hex_to_rgba(initial_color))
        self.color_btn.connect("color-set", self._on_color_set)
        self.append(self.color_btn)

    def _on_hex_changed(self, entry: Gtk.Entry) -> None:
        """Handle hex entry text changes."""
        value = entry.get_text().strip()
        if validate_hex(value) and self.reactive_colors:
            self.reactive_colors.update(self.color_key, value)

    def _on_color_set(self, btn: Gtk.ColorButton) -> None:
        """Handle color picker changes."""
        rgba = btn.get_rgba()
        value = f"#{int(rgba.red*255):02x}{int(rgba.green*255):02x}{int(rgba.blue*255):02x}"
        self.hex_entry.set_text(value)
        if self.reactive_colors:
            self.reactive_colors.update(self.color_key, value)


class ContrastTile(Gtk.Box):
    """Contrast pair: label + bg hex/picker + fg hex/picker.

    Args:
        label: Display label for the row
        bg_color: Initial background color
        fg_color: Initial foreground color
    """

    def __init__(self, label: str, bg_color: str = "#000000", fg_color: str = "#ffffff", **kwargs):
        super().__init__(**kwargs)
        self.set_spacing(8)
        self.set_valign(Gtk.Align.CENTER)

        lbl = Gtk.Label()
        lbl.set_text(label)
        lbl.set_hexpand(False)
        lbl.set_width_chars(14)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_valign(Gtk.Align.START)
        lbl.set_xalign(0)
        self.append(lbl)

        bg_hex = Gtk.Entry()
        bg_hex.set_text(bg_color)
        bg_hex.set_width_chars(8)
        bg_hex.set_hexpand(False)
        self.append(bg_hex)

        bg_btn = Gtk.ColorButton()
        bg_btn.set_rgba(hex_to_rgba(bg_color))
        self.append(bg_btn)

        fg_hex = Gtk.Entry()
        fg_hex.set_text(fg_color)
        fg_hex.set_width_chars(8)
        fg_hex.set_hexpand(False)
        self.append(fg_hex)

        fg_btn = Gtk.ColorButton()
        fg_btn.set_rgba(hex_to_rgba(fg_color))
        self.append(fg_btn)