"""Tests for UI widget utilities (non-GTK)."""

import pytest
from noctalia_color_scheme_manager.ui.widgets.color_tile import hex_to_rgb, hex_to_rgba


class TestColorUtils:
    """Tests for color utility functions."""

    def test_hex_to_rgb_valid(self):
        """Converts valid hex colors to RGB."""
        r, g, b = hex_to_rgb("#ff0000")
        assert r == pytest.approx(1.0)
        assert g == pytest.approx(0.0)
        assert b == pytest.approx(0.0)

    def test_hex_to_rgb_green(self):
        """Converts green hex to RGB."""
        r, g, b = hex_to_rgb("#00ff00")
        assert r == pytest.approx(0.0)
        assert g == pytest.approx(1.0)
        assert b == pytest.approx(0.0)

    def test_hex_to_rgb_blue(self):
        """Converts blue hex to RGB."""
        r, g, b = hex_to_rgb("#0000ff")
        assert r == pytest.approx(0.0)
        assert g == pytest.approx(0.0)
        assert b == pytest.approx(1.0)

    def test_hex_to_rgb_mid_gray(self):
        """Converts mid-gray hex to RGB."""
        r, g, b = hex_to_rgb("#808080")
        assert r == pytest.approx(128 / 255)
        assert g == pytest.approx(128 / 255)
        assert b == pytest.approx(128 / 255)

    def test_hex_to_rgb_invalid_returns_gray(self):
        """Invalid hex returns neutral gray."""
        r, g, b = hex_to_rgb("invalid")
        assert r == pytest.approx(0.5)
        assert g == pytest.approx(0.5)
        assert b == pytest.approx(0.5)

    def test_hex_to_rgb_3_digit_shorthand(self):
        """Converts 3-digit hex shorthand (e.g., #fff -> white)."""
        r, g, b = hex_to_rgb("#fff")
        assert r == pytest.approx(1.0)
        assert g == pytest.approx(1.0)
        assert b == pytest.approx(1.0)

    def test_hex_to_rgb_3_digit_red(self):
        """Converts 3-digit red shorthand."""
        r, g, b = hex_to_rgb("#f00")
        assert r == pytest.approx(1.0)
        assert g == pytest.approx(0.0)
        assert b == pytest.approx(0.0)

    def test_hex_to_rgb_pure_black(self):
        """Converts pure black to (0,0,0)."""
        r, g, b = hex_to_rgb("#000000")
        assert (r, g, b) == (0.0, 0.0, 0.0)

    def test_hex_to_rgb_pure_white(self):
        """Converts pure white to (1,1,1)."""
        r, g, b = hex_to_rgb("#ffffff")
        assert (r, g, b) == (1.0, 1.0, 1.0)

    def test_hex_to_rgb_uppercase(self):
        """Handles uppercase hex."""
        r, g, b = hex_to_rgb("#ABCDEF")
        assert (r, g, b) == pytest.approx((171 / 255, 205 / 255, 239 / 255))

    def test_hex_to_rgba_valid(self):
        """Converts valid hex to GdkRGBA."""
        rgba = hex_to_rgba("#ff0000")
        assert rgba.red == pytest.approx(1.0)
        assert rgba.green == pytest.approx(0.0)
        assert rgba.blue == pytest.approx(0.0)
        assert rgba.alpha == pytest.approx(1.0)

    def test_hex_to_rgba_with_alpha(self):
        """Converts 8-digit hex with alpha to GdkRGBA."""
        rgba = hex_to_rgba("#ff000080")
        assert rgba.red == pytest.approx(1.0)
        assert rgba.green == pytest.approx(0.0)
        assert rgba.blue == pytest.approx(0.0)
        # Alpha is 128/255 ≈ 0.502
        assert rgba.alpha == pytest.approx(128 / 255, rel=0.01)

    def test_hex_to_rgba_3_digit(self):
        """Converts 3-digit hex shorthand to GdkRGBA."""
        rgba = hex_to_rgba("#fff")
        assert rgba.red == pytest.approx(1.0)
        assert rgba.green == pytest.approx(1.0)
        assert rgba.blue == pytest.approx(1.0)

    def test_hex_to_rgba_black(self):
        """Converts pure black hex to GdkRGBA."""
        rgba = hex_to_rgba("#000000")
        assert rgba.red == pytest.approx(0.0)
        assert rgba.green == pytest.approx(0.0)
        assert rgba.blue == pytest.approx(0.0)

    def test_hex_to_rgba_white(self):
        """Converts pure white hex to GdkRGBA."""
        rgba = hex_to_rgba("#ffffff")
        assert rgba.red == pytest.approx(1.0)
        assert rgba.green == pytest.approx(1.0)
        assert rgba.blue == pytest.approx(1.0)