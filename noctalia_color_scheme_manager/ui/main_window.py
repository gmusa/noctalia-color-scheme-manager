"""Main window: sidebar with theme list + content area."""

import gi  # noqa: E401

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gtk  # noqa: E402

from .theme_editor import ThemeEditor

# Default Monokai colors for demo
DARK_COLORS = {
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
}

LIGHT_COLORS = {
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
}


class MainWindow(Adw.Bin):
    """Main window with sidebar for theme list.

    Args:
        theme_name: Initial theme to display (default "monokai")
        dark_colors: Dict with dark variant colors
        light_colors: Dict with light variant colors
    """

    def __init__(
        self,
        theme_name: str = "monokai",
        dark_colors: dict | None = None,
        light_colors: dict | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._theme_name = theme_name
        self._dark_colors = dark_colors or DARK_COLORS
        self._light_colors = light_colors or LIGHT_COLORS

        # Use a paned layout: sidebar fixed width (max 350), content fills rest
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_hexpand(True)

        # Sidebar panel
        sidebar = self._build_sidebar()
        sidebar.set_size_request(200, -1)
        paned.set_start_child(sidebar)
        paned.set_resize_start_child(False)
        paned.set_shrink_start_child(False)

        # Content panel
        editor = ThemeEditor(
            self._theme_name,
            self._dark_colors,
            self._light_colors,
        )
        paned.set_end_child(editor)
        paned.set_resize_end_child(True)
        paned.set_shrink_end_child(False)

        self.set_child(paned)

    def _build_sidebar(self) -> Gtk.Widget:
        """Build the theme list sidebar with max-width."""
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

        for name in ["monokai", "GitHub Dark", "Oxocarbon"]:
            btn = Gtk.ToggleButton()
            btn.set_label(name)
            btn.set_hexpand(True)
            btn.set_halign(Gtk.Align.FILL)
            theme_list.append(btn)

        sidebar.append(theme_list)

        # Spacer to maintain space between theme list and add section
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