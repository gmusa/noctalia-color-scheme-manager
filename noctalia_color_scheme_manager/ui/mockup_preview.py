"""Mockup Preview: functional demo using modular UI components.

This module demonstrates integration of all UI components.
Run with: python -m noctalia_color_scheme_manager.ui.mockup_preview
"""

import sys

from .app import App


def main() -> int:
    """Entry point for the demo."""
    app = App()
    return app.run(sys.argv)


__all__ = ["App", "main"]


if __name__ == "__main__":
    sys.exit(main())
