"""Application: Adw.Application setup."""

import sys

import gi  # noqa: E401

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw  # noqa: E402

from .main_window import MainWindow  # noqa: E402


class App(Adw.Application):
    """Main application for Noctalia Color Scheme Manager.

    Args:
        application_id: GNOME application ID
    """

    def __init__(self, application_id: str = "com.noctalia.ColorSchemeManager", **kwargs):
        super().__init__(application_id=application_id, **kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app: Adw.Application) -> None:
        """Create and present the main window."""
        window = Adw.ApplicationWindow(application=app)
        window.set_title("Noctalia Color Scheme Manager")
        window.set_default_size(1100, 750)

        main = MainWindow()
        window.set_content(main.get_widget())

        window.present()


def main() -> int:
    """Entry point for the application."""
    app = App()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
