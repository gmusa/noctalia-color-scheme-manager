"""Data module for noctalia-color-scheme-manager.

Provides theme management, models, and schema validation.

Public API:
    ThemeManager: Filesystem operations for themes
    ThemeModel: Theme data with signal callbacks
    VariantColors: Material Design tokens for a variant
    TerminalColors: Terminal color palette
    validate_theme: Validate theme data structure
    validate_color: Validate hex color format
    get_default_theme: Get a deep copy of the default Monokai template
"""

from .schema import get_default_theme, validate_color, validate_theme
from .theme_model import ThemeModel, VariantColors, TerminalColors
from .theme_manager import ThemeManager

__all__ = [
    "ThemeManager",
    "ThemeModel",
    "VariantColors",
    "TerminalColors",
    "validate_theme",
    "validate_color",
    "get_default_theme",
]
