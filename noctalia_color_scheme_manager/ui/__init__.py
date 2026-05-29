"""UI module for noctalia-color-scheme-manager.

Components:
    App: Main application (Adw.Application)
    MainWindow: Main window with sidebar
    ThemeEditor: Theme editor with Dark/Light tabs
    VariantPage: Variant page with Material + Terminal cards
"""

from .app import App
from .main_window import MainWindow
from .theme_editor import ThemeEditor
from .variant_page import VariantPage

__all__ = [
    "App",
    "MainWindow",
    "ThemeEditor",
    "VariantPage",
]
