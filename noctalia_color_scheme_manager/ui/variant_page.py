"""Variant page: Material + Terminal cards for Dark/Light variant."""

import gi  # noqa: E401

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk  # noqa: E402

from .widgets.preview import MaterialPreview, ReactiveColors, TerminalPreview
from .editors.material_editor import MaterialEditor
from .editors.terminal_editor import TerminalEditor


class VariantPage(Gtk.Box):
    """Single variant editor: Material + Terminal cards stacked with scroll.

    Uses ReactiveColors for reactive Material preview updates.

    Args:
        reactive_colors: ReactiveColors instance for this variant
        dark_reactive: ReactiveColors for dark variant (for preview contrast)
        light_reactive: ReactiveColors for light variant (for preview contrast)
    """

    def __init__(
        self,
        reactive_colors: ReactiveColors,
        dark_reactive: ReactiveColors,
        light_reactive: ReactiveColors,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.reactive_colors = reactive_colors

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(16)
        self.set_hexpand(True)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(400)
        scrolled.set_max_content_height(600)

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

        mat_editor = MaterialEditor(reactive_colors)
        mat_row.append(mat_editor)

        mat_preview = MaterialPreview(reactive_colors)
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

        term_editor = TerminalEditor(reactive_colors.get_all())
        term_row.append(term_editor)

        term_preview = TerminalPreview(reactive_colors.get_all())
        term_row.append(term_preview)

        term_box.append(term_row)
        content.append(term_box)

        scrolled.set_child(content)
        self.append(scrolled)