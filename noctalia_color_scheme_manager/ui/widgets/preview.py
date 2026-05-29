"""Preview widgets for Material and Terminal themes."""

import gi  # noqa: E401

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, Gtk  # noqa: E402

from .color_tile import darken_color, hex_to_rgb


class ReactiveColors:
    """Observable dictionary of colors with callback on change.

    Components (editors, previews) share this instance. When any color
    changes, it calls all registered callbacks with a copy of the colors dict.

    This is a simple callback-based alternative to GObject signals to avoid
    GObject type registration issues with complex types like dict.
    """

    def __init__(self, colors: dict) -> None:
        self._colors: dict = dict(colors)
        self._callbacks: list[callable] = []

    def connect(self, callback: callable) -> None:
        """Register a callback to be called when colors change."""
        self._callbacks.append(callback)

    def disconnect(self, callback: callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def get(self, key: str, default: str = "#808080") -> str:
        """Get a color value by key."""
        return self._colors.get(key, default)

    def get_all(self) -> dict:
        """Return a copy of the colors dict."""
        return dict(self._colors)

    def update(self, key: str, value: str) -> None:
        """Update a single color and notify callbacks if value changed."""
        if key in self._colors and self._colors[key] == value:
            return  # No-op if value unchanged
        self._colors[key] = value
        colors_copy = self.get_all()
        for callback in self._callbacks:
            callback(colors_copy)


class ChipDrawingArea(Gtk.DrawingArea):
    """Custom DrawingArea for a color chip with hover, outline, and shadow support.

    Properties:
        bg_color: Normal background color
        fg_color: Normal foreground (text) color
        hover_bg: Hover background color (None = auto-darken)
        hover_fg: Hover foreground color (None = use fg_color)
        outline_color: Border color (None = no border)
        shadow_color: Shadow color (None = no shadow)
        label: Text to display (default "Aa")

    Signals:
        hover-changed: Emitted when hover state changes (emits True/False)
    """

    def __init__(  # noqa: PLR0913
        self,
        bg_color: str = "#808080",
        fg_color: str = "#ffffff",
        hover_bg: str | None = None,
        hover_fg: str | None = None,
        outline_color: str | None = None,
        shadow_color: str | None = None,
        label: str = "Aa",
        **kwargs
    ):
        super().__init__(**kwargs)

        # Store properties
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.outline_color = outline_color
        self.shadow_color = shadow_color
        self.label = label

        # Hover state
        self._is_hovering = False

        # Size
        self.set_size_request(60, 40)

        # Draw callback
        self.set_draw_func(self._draw)

        # Hover detection via motion controller (GTK4 compatible)
        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect("enter", self._on_enter)
        motion_controller.connect("leave", self._on_leave)
        self.add_controller(motion_controller)

    def _on_enter(self, controller, x: float, y: float) -> None:
        """Handle mouse enter event."""
        self._is_hovering = True
        self.queue_draw()

    def _on_leave(self, controller) -> None:
        """Handle mouse leave event."""
        self._is_hovering = False
        self.queue_draw()

    def _get_effective_colors(self) -> tuple[str, str]:
        """Return (bg, fg) based on hover state.

        If hover_bg is defined, use it; otherwise auto-darken bg_color.
        If hover_fg is defined, use it; otherwise use fg_color.
        """
        if self._is_hovering:
            bg = self.hover_bg if self.hover_bg else darken_color(self.bg_color)
            fg = self.hover_fg if self.hover_fg else self.fg_color
            return bg, fg
        return self.bg_color, self.fg_color

    def _draw(self, area, cr, w, h, data=None):
        """Draw the chip with current colors and hover state."""
        bg, fg = self._get_effective_colors()

        # Shadow (if defined) - drop shadow offset behind chip
        # Draw shadow FIRST so it appears behind the chip
        if self.shadow_color:
            r, g, b = hex_to_rgb(self.shadow_color)
            # Offset shadow (bottom-right of chip)
            shadow_x = 3
            shadow_y = 3
            shadow_w = w - shadow_x
            shadow_h = h - shadow_y
            # Draw shadow rectangle
            cr.set_source_rgba(r, g, b, 0.6)
            cr.rectangle(shadow_x, shadow_y, shadow_w, shadow_h)
            cr.fill()

        # Main background
        r, g, b = hex_to_rgb(bg)
        cr.set_source_rgb(r, g, b)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        # Outline border (if defined)
        if self.outline_color:
            r, g, b = hex_to_rgb(self.outline_color)
            cr.set_source_rgba(r, g, b, 0.7)
            cr.set_line_width(2)
            cr.rectangle(1, 1, w - 2, h - 2)
            cr.stroke()

        # Text centered
        r, g, b = hex_to_rgb(fg)
        cr.set_source_rgb(r, g, b)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(13)
        extents = cr.text_extents(self.label)
        x = (w - extents.width) / 2
        y = (h + extents.height) / 2 - 2
        cr.move_to(x, y)
        cr.show_text(self.label)


class ColorChip(Gtk.Box):
    """A color chip drawn with cairo.

    Wrapper around ChipDrawingArea that provides a fixed-size container.
    Exposes the ChipDrawingArea properties for reactive updates.
    """

    def __init__(  # noqa: PLR0913
        self,
        bg_color: str = "#808080",
        fg_color: str = "#ffffff",
        hover_bg: str | None = None,
        hover_fg: str | None = None,
        outline_color: str | None = None,
        shadow_color: str | None = None,
        label: str = "Aa",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.set_size_request(65, 45)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)

        # Drawing area for the chip
        self._area = ChipDrawingArea(
            bg_color=bg_color,
            fg_color=fg_color,
            hover_bg=hover_bg,
            hover_fg=hover_fg,
            outline_color=outline_color,
            shadow_color=shadow_color,
            label=label,
        )
        self._area.set_hexpand(True)
        self._area.set_vexpand(True)
        self.append(self._area)

    @property
    def bg_color(self) -> str:
        return self._area.bg_color

    @bg_color.setter
    def bg_color(self, value: str) -> None:
        self._area.bg_color = value
        self._area.queue_draw()

    @property
    def fg_color(self) -> str:
        return self._area.fg_color

    @fg_color.setter
    def fg_color(self, value: str) -> None:
        self._area.fg_color = value
        self._area.queue_draw()

    @property
    def hover_bg(self) -> str | None:
        return self._area.hover_bg

    @hover_bg.setter
    def hover_bg(self, value: str | None) -> None:
        self._area.hover_bg = value
        self._area.queue_draw()

    @property
    def hover_fg(self) -> str | None:
        return self._area.hover_fg

    @hover_fg.setter
    def hover_fg(self, value: str | None) -> None:
        self._area.hover_fg = value
        self._area.queue_draw()

    @property
    def outline_color(self) -> str | None:
        return self._area.outline_color

    @outline_color.setter
    def outline_color(self, value: str | None) -> None:
        self._area.outline_color = value
        self._area.queue_draw()

    @property
    def shadow_color(self) -> str | None:
        return self._area.shadow_color

    @shadow_color.setter
    def shadow_color(self, value: str | None) -> None:
        self._area.shadow_color = value
        self._area.queue_draw()


class ColorRow(Gtk.Box):
    """A row showing a color with its 4 style variants.

    Uses ReactiveColors for reactive updates and hover support.
    """

    def __init__(  # noqa: PLR0913
        self,
        label: str,
        reactive_colors: ReactiveColors,
        color_key: str,
        on_key: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(4)
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.CENTER)

        self.reactive_colors = reactive_colors
        self.color_key = color_key
        self.on_key = on_key
        self.chips: list[ColorChip] = []

        # Connect to reactive colors
        self.reactive_colors.connect(self._on_colors_changed)

        # Label
        name_lbl = Gtk.Label()
        name_lbl.set_text(label)
        name_lbl.set_size_request(80, -1)
        name_lbl.set_halign(Gtk.Align.END)
        name_lbl.set_valign(Gtk.Align.CENTER)
        name_lbl.add_css_class("dim-label")
        self.append(name_lbl)

        # Create 4 chips with hover support
        self._create_chips()

    def _create_chips(self) -> None:
        """Create or update the 4 variant chips."""
        colors = self.reactive_colors.get_all()
        bg = colors.get(self.color_key, "#808080")
        fg = colors.get(self.on_key, "#ffffff")
        hover_bg = colors.get("mHover")
        hover_fg = colors.get("mOnHover")

        # Clear existing chips
        for chip in self.chips:
            self.remove(chip)
        self.chips.clear()

        # 4 variants: (no O, no S), (O, no S), (no O, S), (O, S)
        for has_outline, has_shadow in [
            (False, False),
            (True, False),
            (False, True),
            (True, True),
        ]:
            outline_color = colors.get("mOutline") if has_outline else None
            shadow_color = colors.get("mShadow") if has_shadow else None

            chip = ColorChip(
                bg_color=bg,
                fg_color=fg,
                hover_bg=hover_bg,
                hover_fg=hover_fg,
                outline_color=outline_color,
                shadow_color=shadow_color,
            )
            self.chips.append(chip)
            self.append(chip)

    def _on_colors_changed(self, colors: dict) -> None:
        """Handle colors-changed callback from ReactiveColors."""
        bg = colors.get(self.color_key, "#808080")
        fg = colors.get(self.on_key, "#ffffff")
        hover_bg = colors.get("mHover")
        hover_fg = colors.get("mOnHover")
        outline = colors.get("mOutline")
        shadow = colors.get("mShadow")

        for i, (has_outline, has_shadow) in enumerate([
            (False, False),
            (True, False),
            (False, True),
            (True, True),
        ]):
            chip = self.chips[i]
            chip.bg_color = bg
            chip.fg_color = fg
            chip.hover_bg = hover_bg
            chip.hover_fg = hover_fg
            chip.outline_color = outline if has_outline else None
            chip.shadow_color = shadow if has_shadow else None
            chip.queue_draw()


class MaterialPreview(Gtk.Frame):
    """Material Design preview with all color variants.

    Uses ReactiveColors for reactive updates when colors change in the editor.
    """

    def __init__(self, reactive_colors: ReactiveColors, **kwargs):
        super().__init__(**kwargs)
        self.reactive_colors = reactive_colors
        self.rows: list[ColorRow] = []

        self.add_css_class("card")
        self.set_valign(Gtk.Align.START)
        self.set_hexpand(False)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)
        main_box.set_spacing(8)

        # Column headers
        header = Gtk.Box()
        header.set_spacing(4)

        spacer = Gtk.Label()
        spacer.set_text("")
        spacer.set_size_request(86, -1)
        header.append(spacer)

        for variant in ["_", "O", "S", "OS"]:
            lbl = Gtk.Label()
            lbl.set_text(variant)
            lbl.set_halign(Gtk.Align.CENTER)
            lbl.set_size_request(65, -1)
            lbl.add_css_class("caption")
            lbl.add_css_class("dim-label")
            header.append(lbl)

        main_box.append(header)

        # Main colors
        for label, color_key, on_key in [
            ("Primary", "mPrimary", "mOnPrimary"),
            ("Secondary", "mSecondary", "mOnSecondary"),
            ("Tertiary", "mTertiary", "mOnTertiary"),
            ("Error", "mError", "mOnError"),
        ]:
            row = ColorRow(label, reactive_colors, color_key, on_key)
            self.rows.append(row)
            main_box.append(row)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(8)
        sep.set_margin_bottom(8)
        main_box.append(sep)

        # Surface colors
        for label, color_key, on_key in [
            ("Surface", "mSurface", "mOnSurface"),
            ("Surface Var", "mSurfaceVariant", "mOnSurfaceVariant"),
        ]:
            row = ColorRow(label, reactive_colors, color_key, on_key)
            self.rows.append(row)
            main_box.append(row)

        self.set_child(main_box)


class TerminalPreview(Gtk.Frame):
    """Terminal preview frame with simulated command output."""

    def __init__(self, colors: dict, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("card")
        self.set_valign(Gtk.Align.START)
        self.set_hexpand(True)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(4)

        p1 = Gtk.Label()
        p1.set_text("$ ls -la")
        box.append(p1)

        p2 = Gtk.Label()
        p2.set_text("drwxr-xr-x  2 user  staff")
        p2.add_css_class("dim-label")
        box.append(p2)

        self.set_child(box)