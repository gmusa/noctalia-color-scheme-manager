"""Entry point for noctalia-color-scheme-manager."""

import sys


def main() -> int:
    """Run the Noctalia Color Scheme Manager application."""
    from .ui.app import App
    app = App()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
