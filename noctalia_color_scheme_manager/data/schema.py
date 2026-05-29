"""Schema validation for Noctalia theme files."""

import copy
import re
from typing import Any


# Regex pattern for valid hex colors
HEX_COLOR_PATTERN = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")

# Required Material Design token names
MATERIAL_TOKENS = [
    "mPrimary",
    "mOnPrimary",
    "mSecondary",
    "mOnSecondary",
    "mTertiary",
    "mOnTertiary",
    "mError",
    "mOnError",
    "mSurface",
    "mOnSurface",
    "mSurfaceVariant",
    "mOnSurfaceVariant",
    "mOutline",
    "mShadow",
    "mHover",
    "mOnHover",
]

# Required Terminal color names
TERMINAL_COLOR_NAMES = [
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
]

# Special terminal colors (not in normal/bright)
TERMINAL_SPECIAL = [
    "foreground",
    "background",
    "cursor",
    "cursorText",
    "selectionFg",
    "selectionBg",
]


def validate_color(color: str) -> bool:
    """Validate a hex color string.

    Args:
        color: Hex color string (e.g., "#ff0000", "#abc", "#aabbccdd")

    Returns:
        True if valid hex color format, False otherwise
    """
    if not isinstance(color, str):
        return False
    return bool(HEX_COLOR_PATTERN.match(color))


def validate_terminal_colors(terminal: dict[str, Any]) -> list[str]:
    """Validate terminal colors section.

    Args:
        terminal: Dictionary with terminal color data

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check special colors
    for key in TERMINAL_SPECIAL:
        if key in terminal:
            if not validate_color(terminal[key]):
                errors.append(f"terminal.{key}: invalid color '{terminal[key]}'")

    # Check normal colors
    normal = terminal.get("normal", {})
    for color_name in TERMINAL_COLOR_NAMES:
        if color_name in normal:
            if not validate_color(normal[color_name]):
                errors.append(f"terminal.normal.{color_name}: invalid color '{normal[color_name]}'")

    # Check bright colors
    bright = terminal.get("bright", {})
    for color_name in TERMINAL_COLOR_NAMES:
        if color_name in bright:
            if not validate_color(bright[color_name]):
                errors.append(f"terminal.bright.{color_name}: invalid color '{bright[color_name]}'")

    return errors


def validate_variant(variant: dict[str, Any], variant_name: str = "variant") -> list[str]:
    """Validate a variant (dark or light) colors section.

    Args:
        variant: Dictionary with variant color data
        variant_name: Name for error messages

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not isinstance(variant, dict):
        return [f"{variant_name}: must be a dictionary"]

    # Check Material Design tokens
    for token in MATERIAL_TOKENS:
        if token in variant:
            if not validate_color(variant[token]):
                errors.append(f"{variant_name}.{token}: invalid color '{variant[token]}'")

    # Check terminal colors
    if "terminal" in variant:
        terminal_errors = validate_terminal_colors(variant["terminal"])
        for err in terminal_errors:
            errors.append(f"{variant_name}.{err}")

    return errors


def validate_theme(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a complete theme data structure.

    Args:
        data: Dictionary with theme data

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if not isinstance(data, dict):
        return False, ["Theme data must be a dictionary"]

    # Check name
    name = data.get("name", data.get("title"))
    if not name:
        errors.append("Theme must have a 'name' or 'title' field")

    # Check dark variant
    dark = data.get("dark", data.get("darkVariant"))
    if dark:
        dark_errors = validate_variant(dark, "dark")
        errors.extend(dark_errors)
    else:
        errors.append("Theme must have a 'dark' or 'darkVariant' section")

    # Check light variant
    light = data.get("light", data.get("lightVariant"))
    if light:
        light_errors = validate_variant(light, "light")
        errors.extend(light_errors)
    else:
        errors.append("Theme must have a 'light' or 'lightVariant' section")

    return len(errors) == 0, errors


# Default Monokai theme template
DEFAULT_THEME = {
    "name": "Monokai",
    "dark": {
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
    "light": {
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
}


def get_default_theme() -> dict:
    """Get a deep copy of the default Monokai theme.

    Returns:
        Deep copy of DEFAULT_THEME to avoid mutation of the original.
    """
    return copy.deepcopy(DEFAULT_THEME)
