"""Tests for ThemeModel dataclasses."""

import pytest
from noctalia_color_scheme_manager.data import ThemeModel, VariantColors, TerminalColors


class TestTerminalColors:
    """Tests for TerminalColors dataclass."""

    def test_creates_with_defaults(self):
        """TerminalColors has sensible defaults."""
        tc = TerminalColors()
        assert tc.foreground == "#000000"
        assert tc.background == "#ffffff"
        assert "black" in tc.normal
        assert "black" in tc.bright

    def test_creates_with_custom_colors(self):
        """TerminalColors accepts custom color values."""
        tc = TerminalColors(
            foreground="#ff0000",
            background="#00ff00",
            cursor="#0000ff",
        )
        assert tc.foreground == "#ff0000"
        assert tc.background == "#00ff00"
        assert tc.cursor == "#0000ff"

    def test_to_dict(self):
        """TerminalColors.to_dict() returns correct structure."""
        tc = TerminalColors(foreground="#abc", background="#123456")
        data = tc.to_dict()
        assert data["foreground"] == "#abc"
        assert data["background"] == "#123456"
        assert "normal" in data
        assert "bright" in data

    def test_to_dict_returns_copy(self):
        """to_dict() returns independent copies."""
        tc = TerminalColors()
        data = tc.to_dict()
        data["foreground"] = "#MUTATED"
        assert tc.foreground == "#000000"

    def test_from_dict(self):
        """TerminalColors.from_dict() creates correct instance."""
        data = {
            "foreground": "#aabbcc",
            "background": "#112233",
            "normal": {"red": "#ff0000"},
            "bright": {"green": "#00ff00"},
        }
        tc = TerminalColors.from_dict(data)
        assert tc.foreground == "#aabbcc"
        assert tc.background == "#112233"
        assert tc.normal["red"] == "#ff0000"
        assert tc.bright["green"] == "#00ff00"

    def test_from_dict_validates_colors(self):
        """TerminalColors.from_dict() rejects invalid colors."""
        data = {"foreground": "not-a-color"}
        with pytest.raises(ValueError, match="invalid hex color"):
            TerminalColors.from_dict(data)

    def test_from_dict_with_defaults(self):
        """TerminalColors.from_dict() uses defaults for missing keys."""
        tc = TerminalColors.from_dict({})
        assert tc.foreground == "#000000"
        assert tc.background == "#ffffff"


class TestVariantColors:
    """Tests for VariantColors dataclass."""

    def test_creates_with_defaults(self):
        """VariantColors has Material Design defaults."""
        vc = VariantColors()
        assert vc.mPrimary == "#6200ee"
        assert vc.mOnPrimary == "#ffffff"
        assert isinstance(vc.terminal, TerminalColors)

    def test_to_dict(self):
        """VariantColors.to_dict() returns complete structure."""
        vc = VariantColors(mPrimary="#ff0000", mSurface="#00ff00")
        data = vc.to_dict()
        assert data["mPrimary"] == "#ff0000"
        assert data["mSurface"] == "#00ff00"
        assert "terminal" in data

    def test_from_dict(self):
        """VariantColors.from_dict() creates correct instance."""
        data = {
            "mPrimary": "#123456",
            "mSecondary": "#654321",
            "terminal": {"foreground": "#abcdef"},
        }
        vc = VariantColors.from_dict(data)
        assert vc.mPrimary == "#123456"
        assert vc.mSecondary == "#654321"
        assert vc.terminal.foreground == "#abcdef"

    def test_from_dict_validates_colors(self):
        """VariantColors.from_dict() rejects invalid colors."""
        data = {"mPrimary": "invalid"}
        with pytest.raises(ValueError, match="invalid hex color"):
            VariantColors.from_dict(data)

    def test_from_dict_nested_validation(self):
        """VariantColors validates terminal colors too."""
        data = {"terminal": {"foreground": "bad"}}
        with pytest.raises(ValueError, match="terminal.foreground"):
            VariantColors.from_dict(data)


class TestThemeModel:
    """Tests for ThemeModel dataclass."""

    def test_creates_with_name(self):
        """ThemeModel requires a name."""
        tm = ThemeModel(name="My Theme")
        assert tm.name == "My Theme"

    def test_creates_with_variants(self):
        """ThemeModel has dark and light variants."""
        tm = ThemeModel(name="Test")
        assert isinstance(tm.dark, VariantColors)
        assert isinstance(tm.light, VariantColors)

    def test_to_dict(self):
        """ThemeModel.to_dict() returns complete structure."""
        tm = ThemeModel(name="Monokai")
        tm.dark.mPrimary = "#ff0000"
        data = tm.to_dict()
        assert data["name"] == "Monokai"
        assert data["dark"]["mPrimary"] == "#ff0000"
        assert "light" in data

    def test_from_dict(self):
        """ThemeModel.from_dict() creates correct instance."""
        data = {
            "name": "Test Theme",
            "dark": {"mPrimary": "#111111"},
            "light": {"mPrimary": "#eeeeee"},
        }
        tm = ThemeModel.from_dict(data)
        assert tm.name == "Test Theme"
        assert tm.dark.mPrimary == "#111111"
        assert tm.light.mPrimary == "#eeeeee"

    def test_from_yaml_dict_with_variants(self):
        """ThemeModel.from_yaml_dict() handles darkVariant/lightVariant."""
        data = {
            "title": "Noctalia Theme",
            "darkVariant": {"mPrimary": "#000"},
            "lightVariant": {"mPrimary": "#fff"},
        }
        tm = ThemeModel.from_yaml_dict(data)
        assert tm.name == "Noctalia Theme"
        assert tm.dark.mPrimary == "#000"
        assert tm.light.mPrimary == "#fff"


class TestThemeModelSignals:
    """Tests for ThemeModel signal callbacks."""

    def test_on_change_registers_callback(self):
        """on_change() registers a callback."""
        tm = ThemeModel(name="Test")
        calls = []

        def callback(theme):
            calls.append(theme)

        tm.on_change(callback)
        tm._notify_change()
        assert len(calls) == 1
        assert calls[0] is tm

    def test_off_change_removes_callback(self):
        """off_change() removes a registered callback."""
        tm = ThemeModel(name="Test")
        calls = []

        def callback(theme):
            calls.append(theme)

        tm.on_change(callback)
        tm.off_change(callback)
        tm._notify_change()
        assert len(calls) == 0

    def test_clear_callbacks_removes_all(self):
        """clear_callbacks() removes all callbacks."""
        tm = ThemeModel(name="Test")
        tm.on_change(lambda t: None)
        tm.on_change(lambda t: None)
        tm.clear_callbacks()
        tm._notify_change()  # Should not raise

    def test_notify_change_continues_on_exception(self):
        """_notify_change() continues if a callback raises."""
        tm = ThemeModel(name="Test")
        good_calls = []

        def good(theme):
            good_calls.append(theme)

        def bad(theme):
            raise RuntimeError("oops")

        tm.on_change(bad)
        tm.on_change(good)
        tm._notify_change()  # Should not raise
        assert len(good_calls) == 1

    def test_update_color_changes_value(self):
        """update_color() changes the color value."""
        tm = ThemeModel(name="Test")
        tm.update_color("dark", "mPrimary", "#ff0000")
        assert tm.dark.mPrimary == "#ff0000"

    def test_update_color_validates_variant(self):
        """update_color() rejects invalid variants."""
        tm = ThemeModel(name="Test")
        with pytest.raises(ValueError, match="variant must be"):
            tm.update_color("invalid", "mPrimary", "#ff0000")

    def test_update_color_validates_color(self):
        """update_color() rejects invalid colors."""
        tm = ThemeModel(name="Test")
        with pytest.raises(ValueError, match="invalid hex color"):
            tm.update_color("dark", "mPrimary", "bad")

    def test_update_color_validates_token(self):
        """update_color() rejects unknown tokens."""
        tm = ThemeModel(name="Test")
        with pytest.raises(ValueError, match="Unknown token"):
            tm.update_color("dark", "notAToken", "#ff0000")

    def test_update_color_notifies_callback(self):
        """update_color() notifies registered callbacks."""
        tm = ThemeModel(name="Test")
        notified = []

        def callback(theme):
            notified.append(theme.dark.mPrimary)

        tm.on_change(callback)
        tm.update_color("dark", "mPrimary", "#00ff00")
        assert notified == ["#00ff00"]

    def test_update_color_terminal(self):
        """update_color() works for terminal colors."""
        tm = ThemeModel(name="Test")
        tm.update_color("dark", "foreground", "#abcdef")
        assert tm.dark.terminal.foreground == "#abcdef"
