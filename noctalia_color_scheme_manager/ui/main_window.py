"""Main window: sidebar with theme list + content area."""

import logging

import gi  # noqa: E401

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import GObject, Gtk  # noqa: E402

from ..data import SystemThemeLoader, ThemeModel  # noqa: E402
from .theme_editor import ThemeEditor  # noqa: E402


class MainWindow(GObject.Object):
    """Main window with sidebar for theme list.

    Themes are loaded dynamically from ~/.config/noctalia/colorschemes/
    using the SystemThemeLoader.
    """

    def __init__(self, **kwargs: GObject.GObject.ConstructorProperties) -> None:
        """Initialize the main window.

        Loads available themes from the system themes directory and displays
        them in the sidebar. The first theme is selected by default.
        """
        super().__init__(**kwargs)
        self._theme_loader = SystemThemeLoader()
        self._theme_buttons: dict[str, Gtk.ToggleButton] = {}
        self._current_theme: ThemeModel | None = None
        self._theme_list_box: Gtk.Box | None = None
        self._empty_label: Gtk.Label | None = None
        self._content_box: Gtk.Box | None = None

        # Build the UI
        self._widget = self._build_widget()
        self._load_themes()

    def get_widget(self) -> Gtk.Widget:
        """Get the main widget."""
        return self._widget

    def _load_themes(self) -> None:
        """Load themes from system directory and populate sidebar."""
        themes = self._theme_loader.list_themes()
        self._populate_sidebar(themes)

        # Auto-select first theme if available
        if themes:
            self._on_theme_selected(themes[0])

    def _populate_sidebar(self, themes: list[str]) -> None:
        """Populate the sidebar with theme buttons.

        Args:
            themes: List of theme names to display
        """
        if self._theme_list_box is None:
            return

        # Clear existing buttons
        for btn in list(self._theme_buttons.values()):
            self._theme_list_box.remove(btn)
        self._theme_buttons.clear()

        if self._empty_label is None:
            return

        if not themes:
            # Show empty state message
            self._empty_label.set_visible(True)
        else:
            self._empty_label.set_visible(False)
            for name in themes:
                btn = Gtk.ToggleButton()
                btn.set_label(name)
                btn.set_hexpand(True)
                btn.set_halign(Gtk.Align.FILL)
                btn.connect("clicked", self._on_button_clicked, name)
                self._theme_list_box.append(btn)
                self._theme_buttons[name] = btn

    def _on_button_clicked(self, btn: Gtk.ToggleButton, theme_name: str) -> None:
        """Handle theme button click.

        Args:
            btn: The clicked button
            theme_name: Name of the theme
        """
        if btn.get_active():
            self._on_theme_selected(theme_name)

    def _on_theme_selected(self, name: str) -> None:
        """Load and display the selected theme.

        Args:
            name: Theme directory name
        """
        # Update toggle states
        for theme, btn in self._theme_buttons.items():
            btn.set_active(theme == name)

        try:
            theme = self._theme_loader.load_theme(name)
            self._current_theme = theme
            self._show_editor(theme)
        except (FileNotFoundError, ValueError) as e:
            logging.error("Failed to load theme '%s': %s", name, e)
            # Clear editor on error
            self._show_error(name, str(e))

    def _show_editor(self, theme: ThemeModel) -> None:
        """Display the theme editor with the given theme.

        Args:
            theme: Loaded ThemeModel to display
        """
        if self._content_box is None:
            return

        # Clear content box
        while child := self._content_box.get_first_child():
            self._content_box.remove(child)

        # Create editor with theme colors
        editor = ThemeEditor(
            theme.name,
            theme.dark.to_dict(),
            theme.light.to_dict(),
        )
        self._content_box.append(editor)

    def _show_error(self, theme_name: str, error: str) -> None:
        """Show an error message when theme loading fails.

        Args:
            theme_name: Name of the failed theme
            error: Error message
        """
        if self._content_box is None:
            return

        while child := self._content_box.get_first_child():
            self._content_box.remove(child)

        error_box = Gtk.Box()
        error_box.set_orientation(Gtk.Orientation.VERTICAL)
        error_box.set_spacing(8)
        error_box.set_halign(Gtk.Align.CENTER)
        error_box.set_valign(Gtk.Align.CENTER)

        icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
        icon.set_pixel_size(48)
        error_box.append(icon)

        label = Gtk.Label()
        label.set_markup(f"<b>Failed to load theme</b>\n{theme_name}")
        error_box.append(label)

        detail = Gtk.Label()
        detail.set_text(error)
        detail.add_css_class("dim-label")
        error_box.append(detail)

        self._content_box.append(error_box)

    def _build_widget(self) -> Gtk.Widget:
        """Build the complete widget tree."""
        # Use a paned layout: sidebar fixed width, content fills rest
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_hexpand(True)

        # Sidebar panel
        sidebar = self._build_sidebar()
        sidebar.set_size_request(200, -1)
        paned.set_start_child(sidebar)
        paned.set_resize_start_child(False)
        paned.set_shrink_start_child(False)

        # Content panel
        content = Gtk.Box()
        content.set_orientation(Gtk.Orientation.VERTICAL)
        content.set_hexpand(True)
        content.set_vexpand(True)
        self._content_box = content

        paned.set_end_child(content)
        paned.set_resize_end_child(True)
        paned.set_shrink_end_child(False)

        return paned

    def _build_sidebar(self) -> Gtk.Widget:
        """Build the theme list sidebar."""
        container = Gtk.Box()
        container.set_orientation(Gtk.Orientation.VERTICAL)
        container.add_css_class("sidebar")

        sidebar = Gtk.Box()
        sidebar.set_orientation(Gtk.Orientation.VERTICAL)
        sidebar.set_valign(Gtk.Align.FILL)
        sidebar.set_vexpand(True)

        # Header
        sidebar_header = Gtk.Box()
        sidebar_header.set_spacing(8)
        sidebar_header.set_margin_start(16)
        sidebar_header.set_margin_end(16)
        sidebar_header.set_margin_top(12)
        sidebar_header.set_margin_bottom(12)

        sidebar_title = Gtk.Label()
        sidebar_title.set_text("Noctalia Colors")
        sidebar_title.add_css_class("title-4")
        sidebar_header.append(sidebar_title)
        sidebar.append(sidebar_header)

        # Theme list
        theme_list = Gtk.Box()
        theme_list.set_orientation(Gtk.Orientation.VERTICAL)
        theme_list.set_spacing(4)
        theme_list.set_margin_start(16)
        theme_list.set_margin_end(16)
        theme_list.set_hexpand(True)
        self._theme_list_box = theme_list

        sidebar.append(theme_list)

        # Empty state label
        empty_label = Gtk.Label()
        empty_label.set_markup(
            "No themes found\n<small>Add themes to ~/.config/noctalia/colorschemes/</small>"
        )
        empty_label.add_css_class("dim-label")
        empty_label.set_visible(False)
        empty_label.set_margin_start(16)
        empty_label.set_margin_end(16)
        empty_label.set_wrap(True)
        self._empty_label = empty_label
        sidebar.append(empty_label)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        sidebar.append(spacer)

        # Border separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(8)
        sep.set_margin_bottom(19)
        sidebar.append(sep)

        # New theme entry row at bottom
        new_box = Gtk.Box()
        new_box.set_spacing(8)
        new_box.set_valign(Gtk.Align.END)
        new_box.set_hexpand(True)
        new_box.set_margin_start(16)
        new_box.set_margin_end(16)
        new_box.set_margin_bottom(16)

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

        container.append(sidebar)
        return container
