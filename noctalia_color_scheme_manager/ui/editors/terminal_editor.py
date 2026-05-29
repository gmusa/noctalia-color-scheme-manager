"""Terminal colors editor widget."""

import gi  # noqa: E401

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")  # noqa: F401

from gi.repository import Gtk  # noqa: E402

from ..widgets.color_tile import ColorTile  # noqa: E402

TERMINAL_COLORS = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


class TerminalEditor(Gtk.Box):
    """Terminal colors section with grid layout.

    Args:
        colors: Dict with terminal color tokens including 'terminal' sub-dict
    """

    def __init__(self, colors: dict, **kwargs):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(8)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(16)
        self.set_margin_bottom(16)

        term = colors.get("terminal", {})
        normal_colors = term.get("normal", {})
        bright_colors = term.get("bright", {})

        # Grid for terminal colors
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(8)

        # Header row
        normal_header = Gtk.Label()
        normal_header.set_text("Normal")
        normal_header.add_css_class("caption")
        normal_header.set_halign(Gtk.Align.START)
        normal_header.set_valign(Gtk.Align.CENTER)
        normal_header.set_hexpand(True)
        grid.attach(normal_header, 1, 0, 1, 1)

        bright_header = Gtk.Label()
        bright_header.set_text("Bright")
        bright_header.add_css_class("caption")
        bright_header.set_halign(Gtk.Align.START)
        bright_header.set_valign(Gtk.Align.CENTER)
        bright_header.set_hexpand(True)
        grid.attach(bright_header, 2, 0, 1, 1)

        # Color rows
        for i, color_key in enumerate(TERMINAL_COLORS):
            row = i + 1

            row_label = Gtk.Label()
            row_label.set_text(color_key.capitalize())
            row_label.set_halign(Gtk.Align.START)
            row_label.set_valign(Gtk.Align.CENTER)
            row_label.set_hexpand(True)
            grid.attach(row_label, 0, row, 1, 1)

            normal_tile = ColorTile(
                label=color_key.capitalize(),
                color_key=f"terminal.normal.{color_key}",
                initial_color=normal_colors.get(color_key, "#000000"),
                show_label=False,
            )
            grid.attach(normal_tile, 1, row, 1, 1)

            bright_tile = ColorTile(
                label=color_key.capitalize(),
                color_key=f"terminal.bright.{color_key}",
                initial_color=bright_colors.get(color_key, "#000000"),
                show_label=False,
            )
            grid.attach(bright_tile, 2, row, 1, 1)

        # Separator row (row 9)
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_hexpand(True)
        sep.set_margin_top(16)
        sep.set_margin_bottom(8)
        grid.attach(sep, 0, 9, 3, 1)

        # Special header row (row 10)
        special_label = Gtk.Label()
        special_label.set_text("Special")
        special_label.add_css_class("caption")
        special_label.set_halign(Gtk.Align.START)
        special_label.set_valign(Gtk.Align.CENTER)
        special_label.set_hexpand(True)
        grid.attach(special_label, 1, 10, 1, 1)

        special_header = Gtk.Label()
        special_header.set_text("")
        special_header.set_hexpand(True)
        grid.attach(special_header, 2, 10, 1, 1)

        # Special items (rows 11-15)
        special_items = ["foreground", "background", "cursor", "selectionFg", "selectionBg"]
        for i, key in enumerate(special_items):
            row = i + 11

            item_label = Gtk.Label()
            item_label.set_text(key)
            item_label.set_halign(Gtk.Align.START)
            item_label.set_valign(Gtk.Align.CENTER)
            item_label.set_hexpand(True)
            grid.attach(item_label, 0, row, 1, 1)

            special_tile = ColorTile(
                label=key,
                color_key=f"terminal.{key}",
                initial_color=term.get(key, "#000000"),
                show_label=False,
            )
            grid.attach(special_tile, 1, row, 1, 1)

            empty = Gtk.Label()
            grid.attach(empty, 2, row, 1, 1)

        self.append(grid)
