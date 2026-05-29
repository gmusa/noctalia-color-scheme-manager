"""System theme loader: scan directories and load themes for UI display."""

import json
import logging
from pathlib import Path
from typing import Optional

import yaml

from .theme_model import ThemeModel


class SystemThemeLoader:
    """Loads themes from ~/.config/noctalia/colorschemes/ for UI display.

    Themes are stored in subdirectories, where each subdirectory contains
    a JSON file (preferred) or YAML file with the same name as the directory.

    Example structure:
        ~/.config/noctalia/colorschemes/
            monokai/
                monokai.json
            GitHub Dark/
                GitHub Dark.json
    """

    THEMES_DIR = Path("~/.config/noctalia/colorschemes").expanduser()

    def __init__(self, themes_dir: Optional[Path] = None) -> None:
        """Initialize the loader.

        Args:
            themes_dir: Optional custom themes directory.
                Defaults to ~/.config/noctalia/colorschemes
        """
        self._themes_dir = themes_dir or self.THEMES_DIR

    @property
    def themes_dir(self) -> Path:
        """Get the themes directory path."""
        return self._themes_dir

    def list_themes(self) -> list[str]:
        """Scan themes directory and return sorted theme names.

        Returns:
            Alphabetically sorted list of theme directory names.
            Returns empty list if themes directory doesn't exist.
        """
        themes = []
        if not self._themes_dir.is_dir():
            logging.debug("Themes directory does not exist: %s", self._themes_dir)
            return themes

        for entry in self._themes_dir.iterdir():
            if not entry.is_dir():
                continue
            if entry.name.startswith("."):
                continue

            # Skip symlinks for security
            if entry.is_symlink():
                logging.warning("Skipping symlink in themes directory: %s", entry.name)
                continue

            # Check for .json or .yaml/.yml file inside
            has_json = (entry / f"{entry.name}.json").exists()
            has_yaml = (entry / f"{entry.name}.yaml").exists() or (
                entry / f"{entry.name}.yml"
            ).exists()

            if has_json or has_yaml:
                themes.append(entry.name)
            else:
                logging.warning(
                    "Theme directory '%s' has no matching theme file", entry.name
                )

        return sorted(themes, key=lambda x: x.lower())

    def load_theme(self, name: str) -> ThemeModel:
        """Load theme by directory name.

        Args:
            name: Theme directory name

        Returns:
            ThemeModel with loaded colors

        Raises:
            FileNotFoundError: Theme directory doesn't exist or no valid file
            ValueError: Theme file is invalid or cannot be parsed
        """
        # Security: reject path traversal
        if ".." in name or "/" in name or "\\" in name:
            raise ValueError(f"Invalid theme name: {name}")

        theme_dir = self._themes_dir / name

        if not theme_dir.is_dir():
            raise FileNotFoundError(f"Theme directory '{name}' not found")

        if theme_dir.is_symlink():
            raise ValueError(f"Theme directory '{name}' is a symlink")

        # Try JSON first, then YAML
        json_path = theme_dir / f"{name}.json"
        yaml_path = theme_dir / f"{name}.yaml"
        yml_path = theme_dir / f"{name}.yml"

        file_path: Optional[Path] = None
        if json_path.exists() and not json_path.is_symlink():
            file_path = json_path
        elif yaml_path.exists() and not yaml_path.is_symlink():
            file_path = yaml_path
        elif yml_path.exists() and not yml_path.is_symlink():
            file_path = yml_path

        if not file_path:
            raise FileNotFoundError(f"No theme file found in '{name}'")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix == ".json":
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValueError("Theme file must contain an object")

            return ThemeModel.from_dict(data)

        except json.JSONDecodeError as e:
            logging.warning("Failed to parse JSON theme '%s': %s", name, e)
            raise ValueError(f"Invalid JSON in theme '{name}': {e}") from e
        except yaml.YAMLError as e:
            logging.warning("Failed to parse YAML theme '%s': %s", name, e)
            raise ValueError(f"Invalid YAML in theme '{name}': {e}") from e
        except OSError as e:
            logging.warning("Failed to read theme '%s': %s", name, e)
            raise ValueError(f"Cannot read theme file: {e}") from e
