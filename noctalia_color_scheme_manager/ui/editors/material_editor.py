"""Material Design tokens editor widget."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import gi  # noqa: E401

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Gdk  # noqa: E402

from ..widgets.color_tile import ColorSwatch, ColorTile  # noqa: E402

if TYPE_CHECKING:
    from ..widgets.preview import ReactiveColors

MATERIAL_PAIRS = [
    ("Primary", "mPrimary", "mOnPrimary"),
    ("Secondary", "mSecondary", "mOnSecondary"),
    ("Tertiary", "mTertiary", "mOnTertiary"),
    ("Error", "mError", "mOnError"),
    ("Surface", "mSurface", "mOnSurface"),
    ("Surface Variant", "mSurfaceVariant", "mOnSurfaceVariant"),
    ("Hover", "mHover", "mOnHover"),
]

MATERIAL_STANDALONE = [
    ("Outline", "mOutline"),
    ("Shadow", "mShadow"),
]


class MaterialEditor(Gtk.Box):
    """Material Design tokens section with grid layout.

    Uses ReactiveColors to emit changes when user edits colors.

    Args:
        reactive_colors: ReactiveColors instance for reactive updates
    """

    def __init__(self, reactive_colors: ReactiveColors, **kwargs):
        super().__init__(**kwargs)
        self.reactive_colors = reactive_colors

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(8)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(16)
        self.set_margin_bottom(16)

        # Grid for material tokens
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(8)

        # Header row
        bg_header = Gtk.Label()
        bg_header.set_text("Background")
        bg_header.add_css_class("caption")
        bg_header.set_halign(Gtk.Align.START)
        bg_header.set_valign(Gtk.Align.CENTER)
        bg_header.set_hexpand(True)
        grid.attach(bg_header, 1, 0, 1, 1)

        fg_header = Gtk.Label()
        fg_header.set_text("Foreground")
        fg_header.add_css_class("caption")
        fg_header.set_halign(Gtk.Align.START)
        fg_header.set_valign(Gtk.Align.CENTER)
        fg_header.set_hexpand(True)
        grid.attach(fg_header, 2, 0, 1, 1)

        # Contrast pairs rows
        for i, (label, bg_key, fg_key) in enumerate(MATERIAL_PAIRS):
            row = i + 1

            row_label = Gtk.Label()
            row_label.set_text(label)
            row_label.set_halign(Gtk.Align.START)
            row_label.set_valign(Gtk.Align.CENTER)
            row_label.set_hexpand(True)
            grid.attach(row_label, 0, row, 1, 1)

            bg_tile = ColorTile(
                label=bg_key,
                color_key=bg_key,
                reactive_colors=reactive_colors,
                show_label=False,
            )
            grid.attach(bg_tile, 1, row, 1, 1)

            fg_tile = ColorTile(
                label=fg_key,
                color_key=fg_key,
                reactive_colors=reactive_colors,
                show_label=False,
            )
            grid.attach(fg_tile, 2, row, 1, 1)

        # Separator row (row 8)
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_hexpand(True)
        grid.attach(sep, 0, 8, 3, 1)

        # Effects header (row 9)
        effects_label = Gtk.Label()
        effects_label.set_text("Effects")
        effects_label.add_css_class("caption")
        effects_label.set_halign(Gtk.Align.START)
        effects_label.set_valign(Gtk.Align.CENTER)
        effects_label.set_hexpand(True)
        grid.attach(effects_label, 1, 9, 1, 1)

        effects_empty = Gtk.Label()
        effects_empty.set_hexpand(True)
        grid.attach(effects_empty, 2, 9, 1, 1)

        # Effects items (Outline, Shadow) - rows 10-11
        for i, (label, key) in enumerate(MATERIAL_STANDALONE):
            row = i + 10

            item_label = Gtk.Label()
            item_label.set_text(label)
            item_label.set_halign(Gtk.Align.START)
            item_label.set_valign(Gtk.Align.CENTER)
            item_label.set_hexpand(True)
            grid.attach(item_label, 0, row, 1, 1)

            effect_tile = ColorTile(
                label=key,
                color_key=key,
                reactive_colors=reactive_colors,
                show_label=False,
            )
            grid.attach(effect_tile, 1, row, 1, 1)

            empty = Gtk.Label()
            grid.attach(empty, 2, row, 1, 1)

        self.append(grid)