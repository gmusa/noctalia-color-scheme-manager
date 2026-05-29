"""Tests for schema validation."""

import pytest
from noctalia_color_scheme_manager.data import (
    validate_color,
    validate_theme,
    get_default_theme,
)


class TestValidateColor:
    """Tests for validate_color function."""

    def test_valid_6_digit_hex(self):
        """Accepts 6-digit hex colors."""
        assert validate_color("#ff0000") is True
        assert validate_color("#00ff00") is True
        assert validate_color("#0000ff") is True
        assert validate_color("#aabbcc") is True

    def test_valid_3_digit_hex(self):
        """Accepts 3-digit shorthand hex."""
        assert validate_color("#f00") is True
        assert validate_color("#0f0") is True
        assert validate_color("#000") is True

    def test_valid_8_digit_hex(self):
        """Accepts 8-digit hex with alpha."""
        assert validate_color("#ff000080") is True
        assert validate_color("#00000000") is True

    def test_valid_lowercase(self):
        """Accepts lowercase hex."""
        assert validate_color("#abcdef") is True
        assert validate_color("#abc") is True

    def test_valid_uppercase(self):
        """Accepts uppercase hex."""
        assert validate_color("#ABCDEF") is True
        assert validate_color("#ABC") is True

    def test_rejects_invalid_format(self):
        """Rejects non-hex formats."""
        assert validate_color("red") is False
        assert validate_color("rgb(255,0,0)") is False
        assert validate_color("hsl(0,100%,50%)") is False

    def test_rejects_empty_string(self):
        """Rejects empty string."""
        assert validate_color("") is False

    def test_rejects_wrong_length(self):
        """Rejects wrong length hex."""
        assert validate_color("#ff") is False
        assert validate_color("#ffff") is False
        assert validate_color("#fffffff") is False

    def test_rejects_invalid_characters(self):
        """Rejects invalid hex characters."""
        assert validate_color("#gg0000") is False
        assert validate_color("#ff00gg") is False

    def test_rejects_non_string(self):
        """Rejects non-string inputs."""
        assert validate_color(None) is False
        assert validate_color(123) is False
        assert validate_color(["#ff0000"]) is False


class TestValidateTheme:
    """Tests for validate_theme function."""

    def test_valid_full_theme(self):
        """Accepts complete valid theme."""
        data = get_default_theme()
        is_valid, errors = validate_theme(data)
        assert is_valid is True
        assert errors == []

    def test_validates_material_colors(self):
        """Validates Material Design token colors."""
        data = {
            "name": "Test",
            "dark": {"mPrimary": "#ff0000"},
            "light": {"mPrimary": "#0000ff"},
        }
        is_valid, errors = validate_theme(data)
        assert is_valid is True

    def test_rejects_invalid_material_color(self):
        """Rejects invalid Material Design colors."""
        data = {
            "name": "Test",
            "dark": {"mPrimary": "invalid"},
            "light": {},
        }
        is_valid, errors = validate_theme(data)
        assert is_valid is False
        assert any("mPrimary" in e for e in errors)

    def test_rejects_invalid_terminal_color(self):
        """Rejects invalid terminal colors."""
        data = {
            "name": "Test",
            "dark": {"terminal": {"foreground": "bad"}},
            "light": {},
        }
        is_valid, errors = validate_theme(data)
        assert is_valid is False
        assert any("terminal" in e for e in errors)

    def test_rejects_missing_name(self):
        """Rejects theme without name."""
        data = {
            "dark": {},
            "light": {},
        }
        is_valid, errors = validate_theme(data)
        assert is_valid is False
        assert any("name" in e.lower() for e in errors)

    def test_rejects_missing_dark(self):
        """Rejects theme without dark variant."""
        data = {
            "name": "Test",
            "light": {},
        }
        is_valid, errors = validate_theme(data)
        assert is_valid is False
        assert any("dark" in e.lower() for e in errors)

    def test_rejects_missing_light(self):
        """Rejects theme without light variant."""
        data = {
            "name": "Test",
            "dark": {},
        }
        is_valid, errors = validate_theme(data)
        assert is_valid is False
        assert any("light" in e.lower() for e in errors)

    def test_accepts_dark_variant(self):
        """Accepts 'darkVariant' as alias for 'dark'."""
        data = {
            "name": "Test",
            "darkVariant": {"mPrimary": "#fff"},
            "light": {"mPrimary": "#000"},
        }
        is_valid, errors = validate_theme(data)
        assert is_valid is True

    def test_accepts_light_variant(self):
        """Accepts 'lightVariant' as alias for 'light'."""
        data = {
            "name": "Test",
            "dark": {"mPrimary": "#fff"},
            "lightVariant": {"mPrimary": "#000"},
        }
        is_valid, errors = validate_theme(data)
        assert is_valid is True

    def test_rejects_non_dict(self):
        """Rejects non-dict input."""
        is_valid, errors = validate_theme("not a dict")
        assert is_valid is False
        assert "dictionary" in errors[0].lower()


class TestGetDefaultTheme:
    """Tests for get_default_theme function."""

    def test_returns_valid_theme(self):
        """Returns a theme that passes validation."""
        data = get_default_theme()
        is_valid, errors = validate_theme(data)
        assert is_valid is True

    def test_returns_copy(self):
        """Returns independent copy."""
        d1 = get_default_theme()
        d2 = get_default_theme()
        d1["dark"]["mPrimary"] = "#MUTATED"
        assert d2["dark"]["mPrimary"] == "#66d9ef"

    def test_has_required_structure(self):
        """Has all required fields."""
        data = get_default_theme()
        assert "name" in data
        assert "dark" in data
        assert "light" in data
        assert "mPrimary" in data["dark"]
        assert "terminal" in data["dark"]
