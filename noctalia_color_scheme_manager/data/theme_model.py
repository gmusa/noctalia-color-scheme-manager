"""Theme model: dataclasses for theme data with signal callbacks."""

from dataclasses import dataclass, field
from typing import Callable, Any

from .schema import validate_color


def _validate_color_value(value: Any, field_name: str) -> str:
    """Validate and return a color value.

    Args:
        value: The value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated color string

    Raises:
        ValueError: If value is not a valid hex color
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name}: expected str, got {type(value).__name__}")
    if not validate_color(value):
        raise ValueError(f"{field_name}: invalid hex color '{value}'")
    return value


@dataclass
class TerminalColors:
    """Terminal color palette for one variant.

    Attributes:
        foreground: Default foreground color
        background: Default background color
        normal: Dictionary of 8 normal colors (black, red, green, yellow, blue, magenta, cyan, white)
        bright: Dictionary of 8 bright colors
        cursor: Cursor color
        cursorText: Cursor text color
        selectionFg: Selection foreground color
        selectionBg: Selection background color
    """

    foreground: str = "#000000"
    background: str = "#ffffff"
    normal: dict[str, str] = field(default_factory=lambda: {
        "black": "#000000",
        "red": "#ff0000",
        "green": "#00ff00",
        "yellow": "#ffff00",
        "blue": "#0000ff",
        "magenta": "#ff00ff",
        "cyan": "#00ffff",
        "white": "#ffffff",
    })
    bright: dict[str, str] = field(default_factory=lambda: {
        "black": "#555555",
        "red": "#ff5555",
        "green": "#55ff55",
        "yellow": "#ffff55",
        "blue": "#5555ff",
        "magenta": "#ff55ff",
        "cyan": "#55ffff",
        "white": "#ffffff",
    })
    cursor: str = "#ffffff"
    cursorText: str = "#000000"
    selectionFg: str = "#ffffff"
    selectionBg: str = "#0000ff"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "foreground": self.foreground,
            "background": self.background,
            "normal": self.normal.copy(),
            "bright": self.bright.copy(),
            "cursor": self.cursor,
            "cursorText": self.cursorText,
            "selectionFg": self.selectionFg,
            "selectionBg": self.selectionBg,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TerminalColors":
        """Create from dictionary with validation.

        Args:
            data: Dictionary with terminal color data

        Returns:
            New TerminalColors instance

        Raises:
            ValueError: If any color value is invalid
        """
        def get_color(key: str, default: str) -> str:
            value = data.get(key, default)
            return _validate_color_value(value, f"terminal.{key}")

        def get_nested_color(group: dict, key: str, default: str) -> str:
            value = group.get(key, default)
            return _validate_color_value(value, f"terminal.{group_name}.{key}")

        normal = {}
        group_name = "normal"
        for color_name in ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]:
            normal[color_name] = get_nested_color(data.get("normal", {}), color_name, "#000000")

        bright = {}
        group_name = "bright"
        for color_name in ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]:
            bright[color_name] = get_nested_color(data.get("bright", {}), color_name, "#555555")

        return cls(
            foreground=get_color("foreground", "#000000"),
            background=get_color("background", "#ffffff"),
            normal=normal,
            bright=bright,
            cursor=get_color("cursor", "#ffffff"),
            cursorText=get_color("cursorText", "#000000"),
            selectionFg=get_color("selectionFg", "#ffffff"),
            selectionBg=get_color("selectionBg", "#0000ff"),
        )


@dataclass
class VariantColors:
    """Material Design tokens + Terminal colors for one variant (Dark or Light).

    Material tokens follow the Material Design 3 color system with on-* variants
    for contrast pairs (e.g., mPrimary/mOnPrimary).
    """

    # Material Design tokens
    mPrimary: str = "#6200ee"
    mOnPrimary: str = "#ffffff"
    mSecondary: str = "#03dac6"
    mOnSecondary: str = "#000000"
    mTertiary: str = "#7c4dff"
    mOnTertiary: str = "#ffffff"
    mError: str = "#b00020"
    mOnError: str = "#ffffff"
    mSurface: str = "#ffffff"
    mOnSurface: str = "#000000"
    mSurfaceVariant: str = "#e7e0ec"
    mOnSurfaceVariant: str = "#49454f"
    mOutline: str = "#79747e"
    mShadow: str = "#000000"
    mHover: str = "#f4f4f4"
    mOnHover: str = "#000000"

    # Terminal colors
    terminal: TerminalColors = field(default_factory=TerminalColors)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "mPrimary": self.mPrimary,
            "mOnPrimary": self.mOnPrimary,
            "mSecondary": self.mSecondary,
            "mOnSecondary": self.mOnSecondary,
            "mTertiary": self.mTertiary,
            "mOnTertiary": self.mOnTertiary,
            "mError": self.mError,
            "mOnError": self.mOnError,
            "mSurface": self.mSurface,
            "mOnSurface": self.mOnSurface,
            "mSurfaceVariant": self.mSurfaceVariant,
            "mOnSurfaceVariant": self.mOnSurfaceVariant,
            "mOutline": self.mOutline,
            "mShadow": self.mShadow,
            "mHover": self.mHover,
            "mOnHover": self.mOnHover,
            "terminal": self.terminal.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VariantColors":
        """Create from dictionary with validation.

        Args:
            data: Dictionary with variant color data

        Returns:
            New VariantColors instance

        Raises:
            ValueError: If any color value is invalid
        """
        def get_color(key: str, default: str) -> str:
            value = data.get(key, default)
            return _validate_color_value(value, key)

        return cls(
            mPrimary=get_color("mPrimary", "#6200ee"),
            mOnPrimary=get_color("mOnPrimary", "#ffffff"),
            mSecondary=get_color("mSecondary", "#03dac6"),
            mOnSecondary=get_color("mOnSecondary", "#000000"),
            mTertiary=get_color("mTertiary", "#7c4dff"),
            mOnTertiary=get_color("mOnTertiary", "#ffffff"),
            mError=get_color("mError", "#b00020"),
            mOnError=get_color("mOnError", "#ffffff"),
            mSurface=get_color("mSurface", "#ffffff"),
            mOnSurface=get_color("mOnSurface", "#000000"),
            mSurfaceVariant=get_color("mSurfaceVariant", "#e7e0ec"),
            mOnSurfaceVariant=get_color("mOnSurfaceVariant", "#49454f"),
            mOutline=get_color("mOutline", "#79747e"),
            mShadow=get_color("mShadow", "#000000"),
            mHover=get_color("mHover", "#f4f4f4"),
            mOnHover=get_color("mOnHover", "#000000"),
            terminal=TerminalColors.from_dict(data.get("terminal", {})),
        )


@dataclass
class ThemeModel:
    """Complete theme with Dark and Light variants.

    This is the core data model for the Noctalia Color Scheme Manager.
    It provides signal callbacks for UI synchronization.

    Attributes:
        name: Theme display name
        dark: Dark variant colors
        light: Light variant colors

    Note:
        Register callbacks with `on_change(callback)` to be notified when
        theme data changes. Callbacks are invoked when using `update_color()`.
    """

    name: str
    dark: VariantColors = field(default_factory=VariantColors)
    light: VariantColors = field(default_factory=VariantColors)

    # Signal callbacks for change notification
    _change_callbacks: list[Callable[["ThemeModel"], None]] = field(
        default_factory=list, repr=False
    )

    def on_change(self, callback: Callable[["ThemeModel"], None]) -> None:
        """Register a callback for theme changes.

        Args:
            callback: Function that receives the ThemeModel instance when changed
        """
        self._change_callbacks.append(callback)

    def off_change(self, callback: Callable[["ThemeModel"], None]) -> None:
        """Unregister a callback.

        Args:
            callback: Previously registered callback to remove
        """
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    def clear_callbacks(self) -> None:
        """Remove all registered callbacks."""
        self._change_callbacks.clear()

    def _notify_change(self) -> None:
        """Internal: notify all registered callbacks of a change."""
        for callback in self._change_callbacks:
            try:
                callback(self)
            except Exception:
                # Log but don't halt other callbacks
                pass

    def update_color(self, variant: str, token: str, value: str) -> None:
        """Update a color value and notify callbacks.

        Args:
            variant: 'dark' or 'light'
            token: Color token name (e.g., 'mPrimary', 'foreground')
            value: New hex color value

        Raises:
            ValueError: If variant is invalid, token doesn't exist, or value is invalid
        """
        _validate_color_value(value, f"{variant}.{token}")

        if variant not in ("dark", "light"):
            raise ValueError(f"variant must be 'dark' or 'light', got '{variant}'")

        colors = getattr(self, variant)

        # Check if token is in terminal or variant colors
        if hasattr(colors, token):
            object.__setattr__(colors, token, value)
        elif token in ("foreground", "background", "cursor", "cursorText", "selectionFg", "selectionBg"):
            object.__setattr__(colors.terminal, token, value)
        else:
            raise ValueError(f"Unknown token '{token}' in {variant}")

        self._notify_change()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "dark": self.dark.to_dict(),
            "light": self.light.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ThemeModel":
        """Create from dictionary with validation.

        Args:
            data: Dictionary with theme data

        Returns:
            New ThemeModel instance

        Raises:
            ValueError: If any color value is invalid
        """
        return cls(
            name=data.get("name", "Untitled"),
            dark=VariantColors.from_dict(data.get("dark", {})),
            light=VariantColors.from_dict(data.get("light", {})),
        )

    @classmethod
    def from_yaml_dict(cls, data: dict) -> "ThemeModel":
        """Create from YAML dict with Noctalia schema.

        Handles both 'dark'/'light' keys and 'darkVariant'/'lightVariant' keys.

        Args:
            data: YAML-loaded dictionary

        Returns:
            New ThemeModel instance

        Raises:
            ValueError: If any color value is invalid
        """
        name = data.get("name", data.get("title", "Untitled"))

        # Handle variant key naming differences
        dark_data = data.get("dark", data.get("darkVariant", {}))
        light_data = data.get("light", data.get("lightVariant", {}))

        return cls(
            name=name,
            dark=VariantColors.from_dict(dark_data),
            light=VariantColors.from_dict(light_data),
        )
