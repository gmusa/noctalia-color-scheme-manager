"""Theme manager: filesystem operations for theme storage."""

import os
import re
from pathlib import Path
from typing import Optional

import yaml

from .schema import get_default_theme, validate_theme
from .theme_model import ThemeModel


class ThemeManager:
    """Manager for theme files in ~/.config/noctalia/colorschemes/.

    Handles listing, loading, saving, creating, and deleting themes.
    """

    THEMES_DIR = Path(os.path.realpath("~/.config/noctalia/colorschemes")).expanduser()

    def __init__(self, themes_dir: Optional[Path] = None) -> None:
        """Initialize the theme manager.

        Args:
            themes_dir: Optional custom themes directory. Defaults to ~/.config/noctalia/colorschemes
        """
        if themes_dir:
            # Resolve to real path to prevent symlink attacks
            self._themes_dir = Path(os.path.realpath(themes_dir))
        else:
            self._themes_dir = self.THEMES_DIR

    @property
    def themes_dir(self) -> Path:
        """Get the themes directory path (resolved real path)."""
        return self._themes_dir

    def _ensure_dir(self) -> None:
        """Ensure the themes directory exists."""
        self._themes_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_name(self, name: str) -> str:
        """Convert theme name to a safe filename.

        Args:
            name: Theme display name

        Returns:
            Sanitized filename string

        Raises:
            ValueError: If name contains unsafe characters or path traversal attempts
        """
        # Reject path traversal attempts early
        if ".." in name or "/" in name or "\\" in name:
            raise ValueError("Theme name cannot contain path traversal characters")

        # Only allow alphanumeric, spaces, and hyphens
        safe = re.sub(r"[^a-z0-9\- ]", "", name.lower())
        safe = safe.strip().replace(" ", "-")
        if not safe:
            raise ValueError("Theme name must contain at least one alphanumeric character")
        # Limit length
        return safe[:64]

    def _resolve_path(self, name: str) -> Path:
        """Get and validate the resolved file path for a theme.

        Args:
            name: Theme name

        Returns:
            Resolved Path within themes_dir

        Raises:
            ValueError: If name is invalid or path is outside themes_dir
        """
        safe_name = self._sanitize_name(name)
        path = self._themes_dir / f"{safe_name}.yaml"

        # Ensure the resolved path is within themes_dir
        resolved = path.resolve()
        if not resolved.is_relative_to(self._themes_dir.resolve()):
            raise ValueError(f"Theme path '{path}' is outside themes directory")

        return path

    def _check_path(self, path: Path, operation: str) -> None:
        """Validate a path is safe for the given operation.

        Args:
            path: Path to check
            operation: Name of the operation (for error messages)

        Raises:
            ValueError: If path is a symlink or outside themes_dir
        """
        # Reject symlinks
        if path.is_symlink():
            raise ValueError(f"Cannot {operation}: theme file is a symlink")

        # Ensure path is within themes directory
        resolved = path.resolve()
        if not resolved.is_relative_to(self._themes_dir.resolve()):
            raise ValueError(f"Cannot {operation}: path is outside themes directory")

    def list_themes(self) -> list[str]:
        """List all available themes.

        Returns:
            List of theme names (without .yaml extension)
        """
        self._ensure_dir()
        themes = []
        for path in self._themes_dir.glob("*.yaml"):
            # Skip symlinks for security
            if path.is_symlink():
                continue
            # Skip hidden files
            if path.name.startswith("."):
                continue
            # Skip non-files (shouldn't happen but be safe)
            if not path.is_file():
                continue
            # Remove extension and format nicely
            name = path.stem.replace("-", " ").replace("_", " ")
            themes.append(name)
        return sorted(themes)

    def theme_exists(self, name: str) -> bool:
        """Check if a theme exists.

        Args:
            name: Theme name

        Returns:
            True if theme exists, False otherwise
        """
        path = self._resolve_path(name)
        return path.is_file()

    def load_theme(self, name: str) -> ThemeModel:
        """Load a theme by name.

        Args:
            name: Theme name

        Returns:
            ThemeModel instance

        Raises:
            FileNotFoundError: If theme does not exist
            ValueError: If theme file is invalid or unsafe
        """
        path = self._resolve_path(name)
        self._check_path(path, "load theme")

        if not path.is_file():
            raise FileNotFoundError(f"Theme '{name}' not found")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                raise ValueError(f"Theme '{name}' is empty")

            # Validate the theme structure
            is_valid, errors = validate_theme(data)
            if not is_valid:
                raise ValueError(f"Invalid theme '{name}': {', '.join(errors)}")

            return ThemeModel.from_yaml_dict(data)

        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse theme '{name}': {e}")
        except OSError as e:
            raise ValueError(f"Failed to read theme '{name}': {e}")

    def save_theme(self, theme: ThemeModel) -> None:
        """Save a theme to disk.

        Args:
            theme: ThemeModel instance to save

        Raises:
            ValueError: If theme data is invalid or path is unsafe
        """
        data = theme.to_dict()

        # Validate before saving
        is_valid, errors = validate_theme(data)
        if not is_valid:
            raise ValueError(f"Invalid theme: {', '.join(errors)}")

        self._ensure_dir()
        path = self._resolve_path(theme.name)

        # Check path is safe before writing (always, even for new files)
        # This prevents symlink attacks where a pre-placed symlink points
        # to an arbitrary location
        if path.is_symlink():
            raise ValueError("Cannot save theme: a symlink exists at the target path")

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def create_theme(self, name: str, template: str = "monokai") -> ThemeModel:
        """Create a new theme from a template.

        Args:
            name: Name for the new theme
            template: Template name to use (only "monokai" supported currently)

        Returns:
            New ThemeModel instance

        Raises:
            ValueError: If template is not supported or theme name already exists
        """
        if self.theme_exists(name):
            raise ValueError(f"Theme '{name}' already exists")

        if template == "monokai":
            # Create theme from deep copy of default Monokai template
            data = get_default_theme()
            data["name"] = name
            theme = ThemeModel.from_yaml_dict(data)
        else:
            raise ValueError(f"Template '{template}' not supported")

        # Save to disk
        self.save_theme(theme)
        return theme

    def delete_theme(self, name: str) -> None:
        """Delete a theme.

        Args:
            name: Theme name to delete

        Raises:
            FileNotFoundError: If theme does not exist
            ValueError: If path is a symlink or unsafe
        """
        path = self._resolve_path(name)
        self._check_path(path, "delete theme")

        if not path.is_file():
            raise FileNotFoundError(f"Theme '{name}' not found")

        path.unlink()

    def rename_theme(self, old_name: str, new_name: str) -> ThemeModel:
        """Rename a theme.

        Args:
            old_name: Current theme name
            new_name: New theme name

        Returns:
            Updated ThemeModel instance

        Raises:
            FileNotFoundError: If theme does not exist
            ValueError: If new name already exists or paths are unsafe
        """
        if self.theme_exists(new_name):
            raise ValueError(f"Theme '{new_name}' already exists")

        old_path = self._resolve_path(old_name)
        self._check_path(old_path, "rename theme")

        # Load, update name, save to new path
        theme = self.load_theme(old_name)
        theme.name = new_name

        self.save_theme(theme)

        # Delete old file
        try:
            old_path.unlink()
        except FileNotFoundError:
            pass  # Already deleted or renamed externally

        return theme

    def duplicate_theme(self, source_name: str, new_name: str) -> ThemeModel:
        """Duplicate a theme with a new name.

        Args:
            source_name: Source theme name
            new_name: Name for the duplicate

        Returns:
            New ThemeModel instance

        Raises:
            FileNotFoundError: If source theme does not exist
            ValueError: If new name already exists or paths are unsafe
        """
        if self.theme_exists(new_name):
            raise ValueError(f"Theme '{new_name}' already exists")

        theme = self.load_theme(source_name)
        theme.name = new_name
        self.save_theme(theme)
        return theme
