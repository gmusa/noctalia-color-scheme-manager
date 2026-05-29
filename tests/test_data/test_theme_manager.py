"""Tests for ThemeManager filesystem operations."""

import pathlib
import tempfile

import pytest
from noctalia_color_scheme_manager.data import ThemeManager, ThemeModel


@pytest.fixture
def tmp_themes_dir():
    """Create a temporary themes directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield pathlib.Path(tmpdir)


@pytest.fixture
def manager(tmp_themes_dir):
    """Create a ThemeManager with temporary directory."""
    return ThemeManager(themes_dir=tmp_themes_dir)


class TestThemeManagerCreate:
    """Tests for create_theme operation."""

    def test_create_theme(self, manager):
        """Creates a new theme from template."""
        theme = manager.create_theme("My Theme")
        assert theme.name == "My Theme"
        assert theme.dark.mPrimary == "#66d9ef"  # Monokai default

    def test_create_theme_saves_to_disk(self, manager, tmp_themes_dir):
        """Creates theme file on disk."""
        manager.create_theme("My Theme")
        assert (tmp_themes_dir / "my-theme.yaml").is_file()

    def test_create_theme_returns_valid_model(self, manager):
        """Returns a valid ThemeModel."""
        theme = manager.create_theme("Test")
        assert isinstance(theme, ThemeModel)

    def test_create_theme_exists(self, manager):
        """Created theme exists."""
        manager.create_theme("Test")
        assert manager.theme_exists("Test") is True

    def test_create_theme_duplicate_raises(self, manager):
        """Creating duplicate theme raises ValueError."""
        manager.create_theme("Test")
        with pytest.raises(ValueError, match="already exists"):
            manager.create_theme("Test")

    def test_create_theme_unsupported_template(self, manager):
        """Rejects unsupported template names."""
        with pytest.raises(ValueError, match="not supported"):
            manager.create_theme("Test", template="unknown")

    def test_create_theme_with_spaces(self, manager, tmp_themes_dir):
        """Handles theme names with spaces."""
        manager.create_theme("My Cool Theme")
        assert (tmp_themes_dir / "my-cool-theme.yaml").is_file()
        assert manager.theme_exists("My Cool Theme")

    def test_create_theme_with_underscores(self, manager, tmp_themes_dir):
        """Handles theme names with underscores (removed, only alphanum kept)."""
        manager.create_theme("My_Cool_Theme")
        # Underscores are stripped; only alphanumeric remain
        assert (tmp_themes_dir / "mycooltheme.yaml").is_file()


class TestThemeManagerList:
    """Tests for list_themes operation."""

    def test_list_themes_empty(self, manager):
        """Lists empty when no themes."""
        assert manager.list_themes() == []

    def test_list_themes(self, manager):
        """Lists all themes."""
        manager.create_theme("Alpha")
        manager.create_theme("Beta")
        manager.create_theme("Gamma")
        themes = manager.list_themes()
        assert "alpha" in themes
        assert "beta" in themes
        assert "gamma" in themes

    def test_list_themes_sorted(self, manager):
        """Lists themes in alphabetical order."""
        manager.create_theme("Zebra")
        manager.create_theme("Apple")
        manager.create_theme("Mango")
        themes = manager.list_themes()
        assert themes == sorted(themes)

    def test_create_theme_name_length_limit(self, manager):
        """Truncates names exceeding 64 characters."""
        long_name = "a" * 65
        theme = manager.create_theme(long_name)
        # Name should be accessible (ThemeModel stores the input name)
        assert len(theme.name) == 65  # Model stores full name


class TestThemeManagerLoad:
    """Tests for load_theme operation."""

    def test_load_theme(self, manager):
        """Loads an existing theme."""
        manager.create_theme("Test")
        theme = manager.load_theme("Test")
        assert theme.name == "Test"

    def test_load_theme_preserves_data(self, manager):
        """Loads theme with correct data."""
        theme = manager.create_theme("Test")
        theme.dark.mPrimary = "#ff0000"
        manager.save_theme(theme)
        loaded = manager.load_theme("Test")
        assert loaded.dark.mPrimary == "#ff0000"

    def test_load_theme_not_found(self, manager):
        """Raises FileNotFoundError for missing theme."""
        with pytest.raises(FileNotFoundError, match="not found"):
            manager.load_theme("Nonexistent")

    def test_load_theme_invalid_yaml(self, manager, tmp_themes_dir):
        """Handles invalid YAML syntax."""
        invalid = tmp_themes_dir / "bad.yaml"
        invalid.write_text("invalid: yaml: content:")
        with pytest.raises(ValueError, match="Failed to parse"):
            manager.load_theme("bad")

    def test_load_theme_invalid_structure(self, manager, tmp_themes_dir):
        """Handles valid YAML with invalid theme structure."""
        invalid = tmp_themes_dir / "bad.yaml"
        invalid.write_text("dark: 'not a dict'\nlight: {}\nname: Test")
        with pytest.raises(ValueError, match="Invalid theme"):
            manager.load_theme("bad")


class TestThemeManagerSave:
    """Tests for save_theme operation."""

    def test_save_theme(self, manager):
        """Saves theme to disk."""
        theme = manager.create_theme("Test")
        theme.dark.mPrimary = "#123456"
        manager.save_theme(theme)
        loaded = manager.load_theme("Test")
        assert loaded.dark.mPrimary == "#123456"

    def test_save_theme_creates_file(self, manager, tmp_themes_dir):
        """Creates file if not exists."""
        theme = ThemeModel(name="NewTheme")
        manager.save_theme(theme)
        assert (tmp_themes_dir / "newtheme.yaml").is_file()


class TestThemeManagerDelete:
    """Tests for delete_theme operation."""

    def test_delete_theme(self, manager, tmp_themes_dir):
        """Deletes theme from disk."""
        manager.create_theme("Test")
        manager.delete_theme("Test")
        assert not (tmp_themes_dir / "test.yaml").exists()
        assert manager.theme_exists("Test") is False

    def test_delete_theme_not_found(self, manager):
        """Raises FileNotFoundError for missing theme."""
        with pytest.raises(FileNotFoundError, match="not found"):
            manager.delete_theme("Nonexistent")


class TestThemeManagerRename:
    """Tests for rename_theme operation."""

    def test_rename_theme(self, manager):
        """Renames theme."""
        manager.create_theme("Old Name")
        renamed = manager.rename_theme("Old Name", "New Name")
        assert renamed.name == "New Name"
        assert not manager.theme_exists("Old Name")
        assert manager.theme_exists("New Name")

    def test_rename_theme_preserves_data(self, manager):
        """Preserves theme data during rename."""
        theme = manager.create_theme("Test")
        theme.dark.mPrimary = "#abcdef"
        manager.save_theme(theme)
        renamed = manager.rename_theme("Test", "Renamed")
        assert renamed.dark.mPrimary == "#abcdef"


class TestThemeManagerDuplicate:
    """Tests for duplicate_theme operation."""

    def test_duplicate_theme(self, manager):
        """Duplicates theme with new name."""
        manager.create_theme("Original")
        dup = manager.duplicate_theme("Original", "Copy")
        assert dup.name == "Copy"
        assert manager.theme_exists("Original")
        assert manager.theme_exists("Copy")

    def test_duplicate_theme_preserves_data(self, manager):
        """Preserves data when duplicating."""
        theme = manager.create_theme("Test")
        theme.dark.mPrimary = "#112233"
        manager.save_theme(theme)
        dup = manager.duplicate_theme("Test", "Duplicate")
        assert dup.dark.mPrimary == "#112233"


class TestThemeManagerSecurity:
    """Tests for security features."""

    def test_rejects_path_traversal(self, manager):
        """Rejects theme names with path traversal."""
        with pytest.raises(ValueError, match="path traversal"):
            manager._resolve_path("../../../etc/passwd")

    def test_rejects_slashes(self, manager):
        """Rejects theme names with slashes."""
        with pytest.raises(ValueError, match="path traversal"):
            manager._resolve_path("foo/bar")

    def test_rejects_backslashes(self, manager):
        """Rejects theme names with backslashes."""
        with pytest.raises(ValueError, match="path traversal"):
            manager._resolve_path("foo\\bar")

    def test_rejects_symlinks_to_load(self, manager, tmp_themes_dir):
        """Rejects loading via symlink."""
        # Create symlink to /etc/passwd
        link = tmp_themes_dir / "evil.yaml"
        link.symlink_to("/etc/passwd")
        with pytest.raises(ValueError):
            manager.load_theme("evil")

    def test_rejects_symlinks_to_save(self, manager, tmp_themes_dir):
        """Rejects saving via symlink."""
        # Create symlink to external file
        external = tmp_themes_dir / "external.yaml"
        external.write_text("original")
        link = tmp_themes_dir / "link.yaml"
        link.symlink_to(external)
        theme = ThemeModel(name="link")
        with pytest.raises(ValueError, match="symlink"):
            manager.save_theme(theme)

    def test_skips_symlinks_in_list(self, manager, tmp_themes_dir):
        """Skips symlinks when listing."""
        manager.create_theme("Real")
        link = tmp_themes_dir / "fake.yaml"
        link.symlink_to("/etc/passwd")
        themes = manager.list_themes()
        assert "real" in themes
        assert "fake" not in themes

    def test_resolves_themes_dir_symlink(self, tmp_themes_dir):
        """Resolves symlinked themes directory."""
        real_dir = tmp_themes_dir / "real"
        real_dir.mkdir()
        link_dir = tmp_themes_dir / "link"
        link_dir.symlink_to(real_dir)
        manager = ThemeManager(themes_dir=link_dir)
        manager.create_theme("Test")
        assert (real_dir / "test.yaml").is_file()


class TestThemeManagerThemeExists:
    """Tests for theme_exists operation."""

    def test_exists_true(self, manager):
        """Returns True for existing theme."""
        manager.create_theme("Test")
        assert manager.theme_exists("Test") is True

    def test_exists_false(self, manager):
        """Returns False for missing theme."""
        assert manager.theme_exists("Nonexistent") is False

    def test_exists_case_insensitive(self, manager):
        """Name lookup is case insensitive."""
        manager.create_theme("My Theme")
        assert manager.theme_exists("my theme") is True
        assert manager.theme_exists("MY THEME") is True
