"""Theme editor: Dark/Light tabs with action buttons."""

import gi  # noqa: E401

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gtk  # noqa: E402

from .widgets.preview import MaterialPreview, ReactiveColors, TerminalPreview
from .editors.material_editor import MaterialEditor
from .editors.terminal_editor import TerminalEditor


class ThemeEditor(Gtk.Box):
    """Main theme editor with Dark/Light tabs and fixed footer.

    Args:
        theme_name: Display name of the theme
        dark_colors: Dict with dark variant colors
        light_colors: Dict with light variant colors
    """

    def __init__(self, theme_name: str, dark_colors: dict, light_colors: dict, **kwargs):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(0)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Create reactive color stores for dark and light variants
        self.dark_reactive = ReactiveColors(dark_colors)
        self.light_reactive = ReactiveColors(light_colors)

        # Header: title + tabs (fixed at top)
        header = Gtk.Box()
        header.set_orientation(Gtk.Orientation.VERTICAL)
        header.set_spacing(8)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(16)
        header.set_hexpand(True)

        title = Gtk.Label()
        title.set_markup(f"<b>{theme_name}</b>")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        header.append(title)

        # Tabs
        stack = Gtk.Stack()
        stack.set_hexpand(True)
        stack.set_vexpand(True)

        # Dark page
        dark_page = _build_variant_page(self.dark_reactive)
        stack.add_titled(dark_page, "dark", "Dark")

        # Light page
        light_page = _build_variant_page(self.light_reactive)
        stack.add_titled(light_page, "light", "Light")

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(stack)

        switcher_wrapper = Gtk.Box()
        switcher_wrapper.set_halign(Gtk.Align.START)
        switcher_wrapper.append(switcher)

        header.append(switcher_wrapper)
        self.append(header)

        self.append(stack)

        # Footer (fixed at bottom)
        footer = Gtk.Box()
        footer.set_orientation(Gtk.Orientation.VERTICAL)
        footer.set_spacing(8)
        footer.set_halign(Gtk.Align.FILL)
        footer.set_margin_start(0)
        footer.set_margin_end(0)
        footer.set_margin_bottom(16)
        footer.set_margin_top(16)
        footer.set_hexpand(True)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(8)
        sep.set_margin_bottom(8)
        footer.append(sep)

        buttons = Gtk.Box()
        buttons.set_spacing(8)
        buttons.set_margin_start(16)
        buttons.set_margin_end(16)

        for label, style in [
            ("Save", "suggested-action"),
            ("Export", "flat"),
            ("Backup", "flat"),
            ("Check Contrast", "flat"),
        ]:
            btn = Gtk.Button()
            btn.set_label(label)
            btn.add_css_class(style)
            buttons.append(btn)

        footer.append(buttons)
        self.append(footer)


def _build_card(
    title: str,
    reactive_colors: ReactiveColors,
    is_terminal: bool = False,
) -> Gtk.Widget:
    """Build a card with editor and preview side by side."""
    card = Gtk.Box()
    card.set_orientation(Gtk.Orientation.VERTICAL)
    card.add_css_class("card")

    header = Gtk.Label()
    header.set_text(title)
    header.add_css_class("title-5")
    header.set_halign(Gtk.Align.START)
    header.set_margin_start(16)
    header.set_margin_end(16)
    header.set_margin_top(16)
    header.set_margin_bottom(8)
    card.append(header)

    row = Gtk.Box()
    row.set_spacing(16)

    if is_terminal:
        # TerminalEditor shares ReactiveColors with TerminalPreview
        editor = TerminalEditor(reactive_colors)
        preview = TerminalPreview(reactive_colors)
    else:
        # MaterialEditor and MaterialPreview share the same ReactiveColors
        editor = MaterialEditor(reactive_colors)
        preview = MaterialPreview(reactive_colors)
        preview.set_size_request(200, -1)

    row.append(editor)
    row.append(preview)
    card.append(row)

    return card


def _build_variant_page(reactive_colors: ReactiveColors) -> Gtk.Widget:
    """Build a variant page with Material + Terminal cards."""
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_hexpand(True)
    scrolled.set_vexpand(True)
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.set_margin_start(16)
    scrolled.set_margin_end(16)
    scrolled.set_margin_top(8)

    # Limit content width to avoid excessive stretching
    clamp = Adw.Clamp()
    clamp.set_maximum_size(1000)
    clamp.set_tightening_threshold(800)
    clamp.set_hexpand(False)
    clamp.set_halign(Gtk.Align.START)

    content = Gtk.Box()
    content.set_orientation(Gtk.Orientation.VERTICAL)
    content.set_spacing(16)
    content.set_hexpand(True)
    content.set_vexpand(True)

    # Material card
    mat_card = _build_card("Material", reactive_colors)
    content.append(mat_card)

    # Terminal card
    term_card = _build_card("Terminal", reactive_colors, is_terminal=True)
    content.append(term_card)

    clamp.set_child(content)
    scrolled.set_child(clamp)

    return scrolled
