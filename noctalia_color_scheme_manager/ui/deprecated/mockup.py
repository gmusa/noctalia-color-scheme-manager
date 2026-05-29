"""Mockup UI - visual prototype for iteration.

.. deprecated:: 0.2.0
    Use :mod:`noctalia_color_scheme_manager.ui.mockup_preview` instead.
    This module is kept for reference and will be removed in a future version.
"""

import sys

import gi  # noqa: E401

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Adw, Gtk, Gdk  # noqa: E402


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

TERMINAL_COLORS = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def hex_to_rgba(color: str) -> Gdk.RGBA:
    """Parse hex color to GdkRGBA."""
    rgba = Gdk.RGBA()
    rgba.parse(color)
    return rgba


def hex_to_rgb(color: str) -> tuple[float, float, float]:
    """Parse hex color to RGB tuple."""
    if color.startswith("#") and len(color) == 7:
        r = int(color[1:3], 16) / 255
        g = int(color[3:5], 16) / 255
        b = int(color[5:7], 16) / 255
        return (r, g, b)
    return (0.5, 0.5, 0.5)


# ──────────────────────────────────────────────────────────────────────────────
# Widgets
# ──────────────────────────────────────────────────────────────────────────────

class ColorSwatch(Gtk.DrawingArea):
    """Colored square swatch."""

    def __init__(self, color: str, size: int = 28, **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self.set_size_request(size, size)
        self.set_draw_func(self._draw, color)

    @staticmethod
    def _draw(area, cr, w, h, color):
        r, g, b = hex_to_rgb(color)
        cr.set_source_rgb(r, g, b)
        cr.paint()


class ColorTile(Gtk.Box):
    """Single color row: optional label + hex + color picker."""

    def __init__(self, label: str, color: str, show_label: bool = True, **kwargs):
        super().__init__(**kwargs)
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

        hex_entry = Gtk.Entry()
        hex_entry.set_text(color)
        hex_entry.set_width_chars(8)
        hex_entry.set_hexpand(False)
        self.append(hex_entry)

        btn = Gtk.ColorButton()
        btn.set_rgba(hex_to_rgba(color))
        self.append(btn)


class ContrastTile(Gtk.Box):
    """Contrast pair: label + two hex + two pickers."""

    def __init__(self, label: str, bg_color: str, fg_color: str, **kwargs):
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


# ──────────────────────────────────────────────────────────────────────────────
# Editor Sections
# ──────────────────────────────────────────────────────────────────────────────

class MaterialEditor(Gtk.Box):
    """Material Design tokens section with grid layout."""

    def __init__(self, colors: dict, **kwargs):
        super().__init__(**kwargs)
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

            bg_tile = ColorTile(bg_key, colors.get(bg_key, "#000000"), show_label=False)
            grid.attach(bg_tile, 1, row, 1, 1)

            fg_tile = ColorTile(fg_key, colors.get(fg_key, "#ffffff"), show_label=False)
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

        effects_empty = Gtk.Label()  # empty for alignment
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

            effect_tile = ColorTile(key, colors.get(key, "#000000"), show_label=False)
            grid.attach(effect_tile, 1, row, 1, 1)

            empty = Gtk.Label()  # empty to maintain grid alignment
            grid.attach(empty, 2, row, 1, 1)

        self.append(grid)


class TerminalEditor(Gtk.Box):
    """Terminal colors section."""

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

        # Grid for terminal colors: titles + rows aligned
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

        # Color rows: each row has normal_tile | bright_tile
        for i, color_key in enumerate(TERMINAL_COLORS):
            row = i + 1

            label = color_key.capitalize()

            row_label = Gtk.Label()
            row_label.set_text(label)
            row_label.set_halign(Gtk.Align.START)
            row_label.set_valign(Gtk.Align.CENTER)
            row_label.set_hexpand(True)
            grid.attach(row_label, 0, row, 1, 1)

            normal_tile = ColorTile(color_key.capitalize(), normal_colors.get(color_key, "#000000"), show_label=False)
            grid.attach(normal_tile, 1, row, 1, 1)

            bright_tile = ColorTile(color_key.capitalize(), bright_colors.get(color_key, "#000000"), show_label=False)
            grid.attach(bright_tile, 2, row, 1, 1)

        self.append(grid)

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
        special_header.set_text("")  # empty for alignment
        special_header.set_hexpand(True)
        grid.attach(special_header, 2, 10, 1, 1)

        # Special items with same grid structure (rows 11-15)
        special_items = ["foreground", "background", "cursor", "selectionFg", "selectionBg"]
        for i, key in enumerate(special_items):
            row = i + 11

            item_label = Gtk.Label()
            item_label.set_text(key)
            item_label.set_halign(Gtk.Align.START)
            item_label.set_valign(Gtk.Align.CENTER)
            item_label.set_hexpand(True)
            grid.attach(item_label, 0, row, 1, 1)

            special_tile = ColorTile(key, term.get(key, "#000000"), show_label=False)
            grid.attach(special_tile, 1, row, 1, 1)

            empty = Gtk.Label()  # empty to maintain grid alignment
            grid.attach(empty, 2, row, 1, 1)

        self.append(grid)


class PreviewPanel(Gtk.Box):
    """Live preview panel (right side)."""

    def __init__(self, dark_colors: dict, light_colors: dict, **kwargs):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(0)
        self.set_valign(Gtk.Align.START)
        self.set_hexpand(False)
        self.set_size_request(260, -1)
        self.set_margin_start(16)

        # Header
        header = Gtk.Label()
        header.set_text("Preview")
        header.add_css_class("title-4")
        header.set_margin_top(16)
        header.set_margin_bottom(16)
        self.append(header)

        # Material preview (Dark mode)
        mat_lbl = Gtk.Label()
        mat_lbl.set_text("Material")
        mat_lbl.add_css_class("title-6")
        mat_lbl.set_margin_top(16)
        mat_lbl.set_margin_bottom(8)
        self.append(mat_lbl)

        dark_frame = self._build_material_preview(dark_colors, "Dark")
        self.append(dark_frame)

        # Terminal preview
        term_lbl = Gtk.Label()
        term_lbl.set_text("Terminal")
        term_lbl.add_css_class("title-6")
        term_lbl.set_margin_top(16)
        term_lbl.set_margin_bottom(8)
        self.append(term_lbl)

        term_frame = self._build_terminal_preview(dark_colors)
        self.append(term_frame)

    def _build_material_preview(self, colors: dict, label: str) -> Gtk.Frame:
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(8)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        mode = Gtk.Label()
        mode.set_text(label)
        mode.add_css_class("caption")
        box.append(mode)

        btn1 = Gtk.Box()
        btn1.set_spacing(6)
        btn1.set_margin_top(8)
        btn1.set_margin_bottom(8)
        btn1.set_margin_start(12)
        btn1.set_margin_end(12)
        btn1.add_css_class("rounded-sm")

        swatch1 = ColorSwatch(colors.get("mPrimary", "#000000"), 16)
        btn1.append(swatch1)
        lbl1 = Gtk.Label()
        lbl1.set_text("Primary")
        btn1.append(lbl1)
        box.append(btn1)

        btn2 = Gtk.Box()
        btn2.set_spacing(6)
        btn2.set_margin_top(4)
        btn2.set_margin_bottom(8)
        btn2.set_margin_start(12)
        btn2.set_margin_end(12)
        btn2.add_css_class("rounded-sm")

        swatch2 = ColorSwatch(colors.get("mSecondary", "#000000"), 16)
        btn2.append(swatch2)
        lbl2 = Gtk.Label()
        lbl2.set_text("Secondary")
        btn2.append(lbl2)
        box.append(btn2)

        frame = Gtk.Frame()
        frame.add_css_class("card")
        frame.set_child(box)
        return frame

    def _build_terminal_preview(self, colors: dict) -> Gtk.Frame:
        term = colors.get("terminal", {})

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(4)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        p1 = Gtk.Label()
        p1.set_text("$ ls -la")
        box.append(p1)

        p2 = Gtk.Label()
        p2.set_text("drwxr-xr-x  2 user  staff")
        p2.add_css_class("dim-label")
        box.append(p2)

        frame = Gtk.Frame()
        frame.add_css_class("card")
        frame.set_child(box)
        return frame


# ──────────────────────────────────────────────────────────────────────────────
# Variant Page (Dark or Light)
# ──────────────────────────────────────────────────────────────────────────────

class VariantPage(Gtk.Box):
    """Single variant editor: Material + Terminal cards stacked."""

    def __init__(self, colors: dict, dark_colors: dict, light_colors: dict, **kwargs):
        super().__init__(**kwargs)
        self.set_spacing(16)
        self.set_hexpand(True)

        content = Gtk.Box()
        content.set_orientation(Gtk.Orientation.VERTICAL)
        content.set_spacing(16)
        content.set_hexpand(True)

        # Material card
        mat_box = Gtk.Box()
        mat_box.set_orientation(Gtk.Orientation.VERTICAL)
        mat_box.add_css_class("card")
        mat_box.set_margin_top(16)

        mat_header = Gtk.Label()
        mat_header.set_text("Material")
        mat_header.add_css_class("title-5")
        mat_header.set_halign(Gtk.Align.START)
        mat_header.set_margin_start(16)
        mat_header.set_margin_end(16)
        mat_header.set_margin_top(16)
        mat_header.set_margin_bottom(8)
        mat_box.append(mat_header)

        # Material content + preview side by side
        mat_row = Gtk.Box()
        mat_row.set_spacing(16)

        mat_editor = MaterialEditor(colors)
        mat_row.append(mat_editor)

        mat_preview = self._build_material_preview(dark_colors, "Dark")
        mat_row.append(mat_preview)

        mat_box.append(mat_row)
        content.append(mat_box)

        # Terminal card
        term_box = Gtk.Box()
        term_box.set_orientation(Gtk.Orientation.VERTICAL)
        term_box.add_css_class("card")

        term_header = Gtk.Label()
        term_header.set_text("Terminal")
        term_header.add_css_class("title-5")
        term_header.set_halign(Gtk.Align.START)
        term_header.set_margin_start(16)
        term_header.set_margin_end(16)
        term_header.set_margin_top(16)
        term_header.set_margin_bottom(8)
        term_box.append(term_header)

        # Terminal content + preview side by side
        term_row = Gtk.Box()
        term_row.set_spacing(16)

        term_editor = TerminalEditor(colors)
        term_row.append(term_editor)

        term_preview = self._build_terminal_preview(dark_colors)
        term_row.append(term_preview)

        term_box.append(term_row)
        content.append(term_box)

        self.append(content)

    def _build_material_preview(self, colors: dict, label: str) -> Gtk.Frame:
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(8)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        mode = Gtk.Label()
        mode.set_text(label)
        mode.add_css_class("caption")
        box.append(mode)

        btn1 = Gtk.Box()
        btn1.set_spacing(6)
        btn1.set_margin_top(8)
        btn1.set_margin_bottom(8)
        btn1.set_margin_start(12)
        btn1.set_margin_end(12)
        btn1.add_css_class("rounded-sm")

        swatch1 = ColorSwatch(colors.get("mPrimary", "#000000"), 16)
        btn1.append(swatch1)
        lbl1 = Gtk.Label()
        lbl1.set_text("Primary")
        btn1.append(lbl1)
        box.append(btn1)

        btn2 = Gtk.Box()
        btn2.set_spacing(6)
        btn2.set_margin_top(4)
        btn2.set_margin_bottom(8)
        btn2.set_margin_start(12)
        btn2.set_margin_end(12)
        btn2.add_css_class("rounded-sm")

        swatch2 = ColorSwatch(colors.get("mSecondary", "#000000"), 16)
        btn2.append(swatch2)
        lbl2 = Gtk.Label()
        lbl2.set_text("Secondary")
        btn2.append(lbl2)
        box.append(btn2)

        frame = Gtk.Frame()
        frame.add_css_class("card")
        frame.set_child(box)
        return frame

    def _build_terminal_preview(self, colors: dict) -> Gtk.Frame:
        term = colors.get("terminal", {})

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(4)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        p1 = Gtk.Label()
        p1.set_text("$ ls -la")
        box.append(p1)

        p2 = Gtk.Label()
        p2.set_text("drwxr-xr-x  2 user  staff")
        p2.add_css_class("dim-label")
        box.append(p2)

        frame = Gtk.Frame()
        frame.add_css_class("card")
        frame.set_child(box)
        return frame
        content.set_orientation(Gtk.Orientation.VERTICAL)
        content.set_spacing(16)
        content.set_hexpand(True)

        # Material card
        mat_box = Gtk.Box()
        mat_box.set_orientation(Gtk.Orientation.VERTICAL)
        mat_box.add_css_class("card")
        mat_box.set_margin_top(16)

        mat_header = Gtk.Label()
        mat_header.set_text("Material")
        mat_header.add_css_class("title-5")
        mat_header.set_halign(Gtk.Align.START)
        mat_header.set_margin_start(16)
        mat_header.set_margin_end(16)
        mat_header.set_margin_top(16)
        mat_header.set_margin_bottom(8)
        mat_box.append(mat_header)

        # Material content + preview side by side
        mat_row = Gtk.Box()
        mat_row.set_spacing(16)

        mat_editor = MaterialEditor(colors)
        mat_row.append(mat_editor)

        mat_preview = self._build_material_preview(dark_colors, "Dark")
        mat_row.append(mat_preview)

        mat_box.append(mat_row)
        content.append(mat_box)

        # Terminal card
        term_box = Gtk.Box()
        term_box.set_orientation(Gtk.Orientation.VERTICAL)
        term_box.add_css_class("card")

        term_header = Gtk.Label()
        term_header.set_text("Terminal")
        term_header.add_css_class("title-5")
        term_header.set_halign(Gtk.Align.START)
        term_header.set_margin_start(16)
        term_header.set_margin_end(16)
        term_header.set_margin_top(16)
        term_header.set_margin_bottom(8)
        term_box.append(term_header)

        # Terminal content + preview side by side
        term_row = Gtk.Box()
        term_row.set_spacing(16)

        term_editor = TerminalEditor(colors)
        term_row.append(term_editor)

        term_preview = self._build_terminal_preview(dark_colors)
        term_row.append(term_preview)

        term_box.append(term_row)
        content.append(term_box)

        self.append(content)


# ──────────────────────────────────────────────────────────────────────────────
# Theme Editor (with Dark/Light tabs)
# ──────────────────────────────────────────────────────────────────────────────

class ThemeEditor(Gtk.Box):
    """Main theme editor with Dark/Light tabs."""

    def __init__(self, theme_name: str, dark_colors: dict, light_colors: dict, **kwargs):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_hexpand(True)

        title = Gtk.Label()
        title.set_markup(f"<b>{theme_name}</b>")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        self.append(title)

        # Stack with tabs for Dark/Light
        stack = Gtk.Stack()
        stack.set_hexpand(True)

        dark_page = VariantPage(dark_colors, dark_colors, light_colors)
        stack.add_titled(dark_page, "dark", "Dark")

        light_page = VariantPage(light_colors, dark_colors, light_colors)
        stack.add_titled(light_page, "light", "Light")

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(stack)

        switcher_wrapper = Gtk.Box()
        switcher_wrapper.set_halign(Gtk.Align.START)
        switcher_wrapper.append(switcher)

        tab_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        tab_container.append(switcher_wrapper)
        tab_container.append(stack)
        tab_container.set_margin_end(16)
        self.append(tab_container)

        actions = Gtk.Box()
        actions.set_spacing(8)
        actions.set_halign(Gtk.Align.END)
        actions.set_margin_top(8)

        for label, style in [("Save", "suggested-action"), ("Export", "flat"),
                              ("Backup", "flat"), ("Check Contrast", "flat")]:
            btn = Gtk.Button()
            btn.set_label(label)
            btn.add_css_class(style)
            actions.append(btn)

        self.append(actions)


# ──────────────────────────────────────────────────────────────────────────────
# Main Window
# ──────────────────────────────────────────────────────────────────────────────

class MainWindow(Adw.Bin):
    """Main window with sidebar."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_box = Gtk.Box()
        main_box.set_spacing(0)

        # Sidebar
        sidebar = Gtk.Box()
        sidebar.set_orientation(Gtk.Orientation.VERTICAL)
        sidebar.set_size_request(220, -1)
        sidebar.add_css_class("sidebar")

        sidebar_header = Gtk.Box()
        sidebar_header.set_spacing(8)
        sidebar_header.set_margin_start(12)
        sidebar_header.set_margin_end(12)
        sidebar_header.set_margin_top(12)
        sidebar_header.set_margin_bottom(12)

        sidebar_title = Gtk.Label()
        sidebar_title.set_text("Noctalia Colors")
        sidebar_title.add_css_class("title-4")
        sidebar_header.append(sidebar_title)
        sidebar.append(sidebar_header)

        theme_list = Gtk.Box()
        theme_list.set_orientation(Gtk.Orientation.VERTICAL)
        theme_list.set_spacing(4)
        theme_list.set_margin_start(8)
        theme_list.set_margin_end(8)

        for name in ["monokai", "GitHub Dark", "Oxocarbon"]:
            btn = Gtk.ToggleButton()
            btn.set_label(name)
            btn.set_hexpand(True)
            btn.set_halign(Gtk.Align.FILL)
            theme_list.append(btn)

        sidebar.append(theme_list)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(8)
        sep.set_margin_bottom(8)
        sidebar.append(sep)

        new_box = Gtk.Box()
        new_box.set_spacing(8)
        new_box.set_margin_start(12)
        new_box.set_margin_end(12)
        new_box.set_margin_bottom(12)

        new_entry = Gtk.Entry()
        new_entry.set_placeholder_text("New theme name...")
        new_entry.set_hexpand(True)

        new_btn = Gtk.Button()
        new_btn.set_icon_name("list-add-symbolic")
        new_btn.add_css_class("flat")
        new_btn.add_css_class("circular")

        new_box.append(new_entry)
        new_box.append(new_btn)
        sidebar.append(new_box)

        content = Gtk.Box()
        content.set_hexpand(True)

        editor = ThemeEditor(
            "monokai",
            dark_colors={
                "mPrimary": "#66d9ef",
                "mOnPrimary": "#272822",
                "mSecondary": "#a6e22e",
                "mOnSecondary": "#272822",
                "mTertiary": "#ae81ff",
                "mOnTertiary": "#272822",
                "mError": "#f92672",
                "mOnError": "#f8f8f2",
                "mSurface": "#272822",
                "mOnSurface": "#f8f8f2",
                "mSurfaceVariant": "#3e3d32",
                "mOnSurfaceVariant": "#75715e",
                "mOutline": "#75715e",
                "mShadow": "#000000",
                "mHover": "#49483e",
                "mOnHover": "#f8f8f2",
                "terminal": {
                    "foreground": "#f8f8f2",
                    "background": "#272822",
                    "normal": {
                        "black": "#272822",
                        "red": "#f92672",
                        "green": "#a6e22e",
                        "yellow": "#e6db74",
                        "blue": "#66d9ef",
                        "magenta": "#ae81ff",
                        "cyan": "#a1efe4",
                        "white": "#f8f8f2",
                    },
                    "bright": {
                        "black": "#75715e",
                        "red": "#f92672",
                        "green": "#a6e22e",
                        "yellow": "#e6db74",
                        "blue": "#66d9ef",
                        "magenta": "#ae81ff",
                        "cyan": "#a1efe4",
                        "white": "#ffffff",
                    },
                    "cursor": "#f8f8f0",
                    "cursorText": "#272822",
                    "selectionFg": "#f8f8f2",
                    "selectionBg": "#49483e",
                },
            },
            light_colors={
                "mPrimary": "#00a8c6",
                "mOnPrimary": "#ffffff",
                "mSecondary": "#72a818",
                "mOnSecondary": "#ffffff",
                "mTertiary": "#8959a8",
                "mOnTertiary": "#ffffff",
                "mError": "#d12f5b",
                "mOnError": "#ffffff",
                "mSurface": "#fafafa",
                "mOnSurface": "#272822",
                "mSurfaceVariant": "#e8e8e8",
                "mOnSurfaceVariant": "#75715e",
                "mOutline": "#cccccc",
                "mShadow": "#d5d5d5",
                "mHover": "#e8e8e8",
                "mOnHover": "#272822",
                "terminal": {
                    "foreground": "#272822",
                    "background": "#fafafa",
                    "normal": {
                        "black": "#272822",
                        "red": "#d12f5b",
                        "green": "#72a818",
                        "yellow": "#c4a000",
                        "blue": "#00a8c6",
                        "magenta": "#8959a8",
                        "cyan": "#319aa5",
                        "white": "#e8e8e8",
                    },
                    "bright": {
                        "black": "#75715e",
                        "red": "#f92672",
                        "green": "#a6e22e",
                        "yellow": "#e6db74",
                        "blue": "#66d9ef",
                        "magenta": "#ae81ff",
                        "cyan": "#a1efe4",
                        "white": "#fafafa",
                    },
                    "cursor": "#272822",
                    "cursorText": "#fafafa",
                    "selectionFg": "#272822",
                    "selectionBg": "#d5d5d5",
                },
            },
        )

        content.append(editor)

        main_box.append(sidebar)

        sep2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep2.set_margin_top(12)
        sep2.set_margin_bottom(12)
        main_box.append(sep2)

        main_box.append(content)

        self.set_child(main_box)


class App(Adw.Application):
    """Main application."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        window = Adw.ApplicationWindow(application=app)
        window.set_title("Noctalia Color Scheme Manager")
        window.set_default_size(1100, 750)

        main = MainWindow()
        window.set_content(main)

        window.present()


def main() -> int:
    app = App()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())