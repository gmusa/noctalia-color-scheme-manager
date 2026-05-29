"""Preview widgets for Material and Terminal themes."""

import gi  # noqa: E401

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from typing import Callable

from gi.repository import Gtk  # noqa: E402
from .color_tile import darken_color, hex_to_rgb


class ReactiveColors:
    """Observable dictionary of colors with callback on change.

    Components (editors, previews) share this instance. When any color
    changes, it calls all registered callbacks with a copy of the colors dict.

    This is a simple callback-based alternative to GObject signals to avoid
    GObject type registration issues with complex types like dict.
    """

    def __init__(self, colors: dict) -> None:
        self._colors: dict = dict(colors)
        self._callbacks: list[Callable[[dict], None]] = []

    def connect(self, callback: Callable[[dict], None]) -> None:
        """Register a callback to be called when colors change."""
        self._callbacks.append(callback)

    def disconnect(self, callback: Callable[[dict], None]) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def get(self, key: str, default: str = "#808080") -> str:
        """Get a color value by key."""
        return self._colors.get(key, default)

    def get_all(self) -> dict:
        """Return a copy of the colors dict."""
        return dict(self._colors)

    def update(self, key: str, value: str) -> None:
        """Update a single color and notify callbacks if value changed."""
        if key in self._colors and self._colors[key] == value:
            return  # No-op if value unchanged
        self._colors[key] = value
        colors_copy = self.get_all()
        for callback in self._callbacks:
            callback(colors_copy)


class ChipDrawingArea(Gtk.DrawingArea):
    """Custom DrawingArea for a color chip with hover, outline, and shadow support."""

    def __init__(  # noqa: PLR0913
        self,
        bg_color: str = "#808080",
        fg_color: str = "#ffffff",
        hover_bg: str | None = None,
        hover_fg: str | None = None,
        outline_color: str | None = None,
        shadow_color: str | None = None,
        label: str = "Aa",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.outline_color = outline_color
        self.shadow_color = shadow_color
        self.label = label

        self._is_hovering = False
        self.set_size_request(60, 40)
        self.set_draw_func(self._draw)

        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect("enter", self._on_enter)
        motion_controller.connect("leave", self._on_leave)
        self.add_controller(motion_controller)

    def _on_enter(self, controller, x: float, y: float) -> None:
        self._is_hovering = True
        self.queue_draw()

    def _on_leave(self, controller) -> None:
        self._is_hovering = False
        self.queue_draw()

    def _get_effective_colors(self) -> tuple[str, str]:
        if self._is_hovering:
            bg = self.hover_bg if self.hover_bg else darken_color(self.bg_color)
            fg = self.hover_fg if self.hover_fg else self.fg_color
            return bg, fg
        return self.bg_color, self.fg_color

    def _draw(self, area, cr, w, h, data=None):
        bg, fg = self._get_effective_colors()

        if self.shadow_color:
            r, g, b = hex_to_rgb(self.shadow_color)
            cr.set_source_rgba(r, g, b, 0.6)
            cr.rectangle(3, 3, w - 3, h - 3)
            cr.fill()

        r, g, b = hex_to_rgb(bg)
        cr.set_source_rgb(r, g, b)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        if self.outline_color:
            r, g, b = hex_to_rgb(self.outline_color)
            cr.set_source_rgba(r, g, b, 0.7)
            cr.set_line_width(2)
            cr.rectangle(1, 1, w - 2, h - 2)
            cr.stroke()

        r, g, b = hex_to_rgb(fg)
        cr.set_source_rgb(r, g, b)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(13)
        extents = cr.text_extents(self.label)
        x = (w - extents.width) / 2
        y = (h + extents.height) / 2 - 2
        cr.move_to(x, y)
        cr.show_text(self.label)


class ColorChip(Gtk.Box):
    """A color chip drawn with cairo.

    Wrapper around ChipDrawingArea that provides a fixed-size container.
    """

    def __init__(  # noqa: PLR0913
        self,
        bg_color: str = "#808080",
        fg_color: str = "#ffffff",
        hover_bg: str | None = None,
        hover_fg: str | None = None,
        outline_color: str | None = None,
        shadow_color: str | None = None,
        label: str = "Aa",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.set_size_request(65, 45)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)

        self._area = ChipDrawingArea(
            bg_color=bg_color,
            fg_color=fg_color,
            hover_bg=hover_bg,
            hover_fg=hover_fg,
            outline_color=outline_color,
            shadow_color=shadow_color,
            label=label,
        )
        self._area.set_hexpand(True)
        self._area.set_vexpand(True)
        self.append(self._area)

    @property
    def bg_color(self) -> str:
        return self._area.bg_color

    @bg_color.setter
    def bg_color(self, value: str) -> None:
        self._area.bg_color = value
        self._area.queue_draw()

    @property
    def fg_color(self) -> str:
        return self._area.fg_color

    @fg_color.setter
    def fg_color(self, value: str) -> None:
        self._area.fg_color = value
        self._area.queue_draw()

    @property
    def hover_bg(self) -> str | None:
        return self._area.hover_bg

    @hover_bg.setter
    def hover_bg(self, value: str | None) -> None:
        self._area.hover_bg = value
        self._area.queue_draw()

    @property
    def hover_fg(self) -> str | None:
        return self._area.hover_fg

    @hover_fg.setter
    def hover_fg(self, value: str | None) -> None:
        self._area.hover_fg = value
        self._area.queue_draw()

    @property
    def outline_color(self) -> str | None:
        return self._area.outline_color

    @outline_color.setter
    def outline_color(self, value: str | None) -> None:
        self._area.outline_color = value
        self._area.queue_draw()

    @property
    def shadow_color(self) -> str | None:
        return self._area.shadow_color

    @shadow_color.setter
    def shadow_color(self, value: str | None) -> None:
        self._area.shadow_color = value
        self._area.queue_draw()


class ColorRow(Gtk.Box):
    """A row showing a color with its 4 style variants."""

    def __init__(  # noqa: PLR0913
        self, label: str, reactive_colors: ReactiveColors, color_key: str, on_key: str, **kwargs
    ):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(4)
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.CENTER)

        self.reactive_colors = reactive_colors
        self.color_key = color_key
        self.on_key = on_key
        self.chips: list[ColorChip] = []

        self.reactive_colors.connect(self._on_colors_changed)

        name_lbl = Gtk.Label()
        name_lbl.set_text(label)
        name_lbl.set_size_request(80, -1)
        name_lbl.set_halign(Gtk.Align.END)
        name_lbl.set_valign(Gtk.Align.CENTER)
        name_lbl.add_css_class("dim-label")
        self.append(name_lbl)

        self._create_chips()

    def _create_chips(self) -> None:
        colors = self.reactive_colors.get_all()
        bg = colors.get(self.color_key, "#808080")
        fg = colors.get(self.on_key, "#ffffff")
        hover_bg = colors.get("mHover")
        hover_fg = colors.get("mOnHover")

        for chip in self.chips:
            self.remove(chip)
        self.chips.clear()

        for has_outline, has_shadow in [
            (False, False),
            (True, False),
            (False, True),
            (True, True),
        ]:
            outline_color = colors.get("mOutline") if has_outline else None
            shadow_color = colors.get("mShadow") if has_shadow else None

            chip = ColorChip(
                bg_color=bg,
                fg_color=fg,
                hover_bg=hover_bg,
                hover_fg=hover_fg,
                outline_color=outline_color,
                shadow_color=shadow_color,
            )
            self.chips.append(chip)
            self.append(chip)

    def _on_colors_changed(self, colors: dict) -> None:
        bg = colors.get(self.color_key, "#808080")
        fg = colors.get(self.on_key, "#ffffff")
        hover_bg = colors.get("mHover")
        hover_fg = colors.get("mOnHover")
        outline = colors.get("mOutline")
        shadow = colors.get("mShadow")

        for i, (has_outline, has_shadow) in enumerate(
            [
                (False, False),
                (True, False),
                (False, True),
                (True, True),
            ]
        ):
            chip = self.chips[i]
            chip.bg_color = bg
            chip.fg_color = fg
            chip.hover_bg = hover_bg
            chip.hover_fg = hover_fg
            chip.outline_color = outline if has_outline else None
            chip.shadow_color = shadow if has_shadow else None
            chip.queue_draw()


class MaterialPreview(Gtk.Box):
    """Material Design preview with all color variants.

    Background is set to mSurface color.
    Updates reactively when colors change.
    """

    def __init__(self, reactive_colors: ReactiveColors, **kwargs):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.reactive_colors = reactive_colors
        self.rows: list[ColorRow] = []
        self._bg_provider: Gtk.CssProvider | None = None

        self.add_css_class("card")
        self.set_valign(Gtk.Align.START)
        self.set_hexpand(False)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        # Inner box with 8px padding for content
        self.main_box = Gtk.Box()
        self.main_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.main_box.set_spacing(8)
        self.main_box.set_margin_start(8)
        self.main_box.set_margin_end(8)
        self.main_box.set_margin_top(8)
        self.main_box.set_margin_bottom(8)
        self.main_box.set_hexpand(True)
        self.main_box.set_vexpand(True)
        self.main_box.add_css_class("material-preview-inner")

        # Column headers
        header = Gtk.Box()
        header.set_spacing(4)

        spacer = Gtk.Label()
        spacer.set_text("")
        spacer.set_size_request(86, -1)
        header.append(spacer)

        for variant in ["_", "O", "S", "OS"]:
            lbl = Gtk.Label()
            lbl.set_text(variant)
            lbl.set_halign(Gtk.Align.CENTER)
            lbl.set_size_request(65, -1)
            lbl.add_css_class("caption")
            lbl.add_css_class("dim-label")
            header.append(lbl)

        self.main_box.append(header)

        # Main colors
        for label, color_key, on_key in [
            ("Primary", "mPrimary", "mOnPrimary"),
            ("Secondary", "mSecondary", "mOnSecondary"),
            ("Tertiary", "mTertiary", "mOnTertiary"),
            ("Error", "mError", "mOnError"),
        ]:
            row = ColorRow(label, reactive_colors, color_key, on_key)
            self.rows.append(row)
            self.main_box.append(row)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(8)
        sep.set_margin_bottom(8)
        self.main_box.append(sep)

        # Surface colors
        for label, color_key, on_key in [
            ("Surface", "mSurface", "mOnSurface"),
            ("Surface Var", "mSurfaceVariant", "mOnSurfaceVariant"),
        ]:
            row = ColorRow(label, reactive_colors, color_key, on_key)
            self.rows.append(row)
            self.main_box.append(row)

        self.append(self.main_box)

        # Connect for background updates
        self.reactive_colors.connect(self._on_colors_changed)
        self._update_background()

    def _on_colors_changed(self, colors: dict) -> None:
        """Handle reactive colors updates for background."""
        self._update_background()

    def _update_background(self) -> None:
        """Update background color on outer widget with border-radius."""
        colors = self.reactive_colors.get_all()
        surface = colors.get("mSurface", "#ffffff")
        on_surface = colors.get("mOnSurface", "#000000")
        css = f"""
            .material-preview-bg {{
                background-color: {surface};
                color: {on_surface};
                border-radius: 12px;
            }}
            .material-preview-bg label {{
                color: {on_surface};
            }}
        """
        # Reuse or create provider
        if self._bg_provider is None:
            self._bg_provider = Gtk.CssProvider()
            self.get_style_context().add_provider(
                self._bg_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
            self.main_box.get_style_context().add_provider(
                self._bg_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
        self._bg_provider.load_from_data(css.encode())
        self.get_style_context().add_class("material-preview-bg")
        self.main_box.get_style_context().add_class("material-preview-bg")

    def cleanup(self) -> None:
        """Disconnect from reactive colors."""
        self.reactive_colors.disconnect(self._on_colors_changed)


class TerminalPreview(Gtk.Box):
    """Terminal preview simulating exa -l command output.

    Background is set to terminal background color.
    Updates reactively when colors change.
    """

    def __init__(self, reactive_colors: ReactiveColors, **kwargs):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.reactive_colors = reactive_colors
        self._bg_provider: Gtk.CssProvider | None = None

        self.add_css_class("card")
        self.set_valign(Gtk.Align.START)
        self.set_hexpand(True)
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        # Inner box with terminal background and 8px padding
        self.main_box = Gtk.Box()
        self.main_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.main_box.set_spacing(2)
        self.main_box.set_margin_start(8)
        self.main_box.set_margin_end(8)
        self.main_box.set_margin_top(8)
        self.main_box.set_margin_bottom(8)
        self.main_box.set_hexpand(True)
        self.main_box.set_vexpand(True)
        self.main_box.add_css_class("terminal-preview-inner")

        # Title
        title = Gtk.Label()
        title.set_text("Terminal Preview")
        title.add_css_class("title-5")
        title.set_halign(Gtk.Align.START)
        self.main_box.append(title)

        # Content area for sample output
        self.content_box = Gtk.Box()
        self.content_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.content_box.set_spacing(0)
        self.main_box.append(self.content_box)

        self.append(self.main_box)

        # Connect to reactive colors
        self.reactive_colors.connect(self._on_colors_changed)
        self._update_content()

    def _on_colors_changed(self, colors: dict) -> None:
        """Handle reactive colors updates."""
        self._update_content()

    def _update_content(self) -> None:
        """Rebuild content based on current colors."""
        # Clear content
        child = self.content_box.get_first_child()
        while child is not None:
            self.content_box.remove(child)
            child = self.content_box.get_first_child()

        colors = self.reactive_colors.get_all()
        sample_widget = self._build_sample_output(colors)
        self.content_box.append(sample_widget)
        self._update_background()

    def _update_background(self) -> None:
        """Update background color on outer widget with border-radius."""
        colors = self.reactive_colors.get_all()
        # Handle both flat keys (after edits) and nested dict (initial state)
        bg = colors.get("terminal.background") or colors.get("terminal", {}).get(
            "background", "#000000"
        )
        fg = colors.get("terminal.foreground") or colors.get("terminal", {}).get(
            "foreground", "#ffffff"
        )
        css = f"""
            .terminal-preview-bg {{
                background-color: {bg};
                color: {fg};
                border-radius: 12px;
            }}
            .terminal-preview-bg label {{
                color: {fg};
            }}
        """
        # Reuse or create provider
        if self._bg_provider is None:
            self._bg_provider = Gtk.CssProvider()
            self.get_style_context().add_provider(
                self._bg_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
            self.main_box.get_style_context().add_provider(
                self._bg_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
        self._bg_provider.load_from_data(css.encode())
        self.get_style_context().add_class("terminal-preview-bg")
        self.main_box.get_style_context().add_class("terminal-preview-bg")

    def _build_sample_output(self, colors: dict) -> Gtk.Widget:
        """Build simulated exa -l output matching the exact exa color scheme."""
        # Handle both flat keys (after edits) and nested dict (initial state)
        term = colors.get("terminal", {})
        fg = colors.get("terminal.foreground") or term.get("foreground", "#ffffff")
        normal = {}
        bright = {}
        for color_key in ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]:
            # Try flat key first, then nested
            flat_normal = colors.get(f"terminal.normal.{color_key}")
            flat_bright = colors.get(f"terminal.bright.{color_key}")
            normal[color_key] = flat_normal or term.get("normal", {}).get(color_key, "#808080")
            bright[color_key] = flat_bright or term.get("bright", {}).get(color_key, "#808080")

        # Container
        container = Gtk.Box()
        container.set_orientation(Gtk.Orientation.VERTICAL)
        container.set_spacing(0)

        # Helper to get color with fallback
        def c(color_key: str) -> str:
            col = bright.get(color_key)
            if col is None:
                col = normal.get(color_key)
            return col if col else fg

        # exa -l color scheme
        sample_lines = [
            # d rwx r-x r-x  gmusa  staff   -  May 28 15:49 docs
            [
                ("d", c("cyan")),
                (":", c("bright")),
                ("rwx", c("bright")),
                ("-", c("bright")),
                ("r-x", c("bright")),
                ("-", c("bright")),
                ("r-x", c("bright")),
                ("-", c("bright")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                (" ", fg),
                ("-", c("bright")),
                (" ", fg),
                ("May 28 15:49 ", c("cyan")),
                ("docs", c("cyan")),
            ],
            # d rwx r-x r-x  gmusa  staff      -  May 29 15:54 openspec
            [
                ("d", c("cyan")),
                (":", c("bright")),
                ("rwx", c("bright")),
                ("-", c("bright")),
                ("r-x", c("bright")),
                ("-", c("bright")),
                ("r-x", c("bright")),
                ("-", c("bright")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                ("  ", fg),
                ("-", c("bright")),
                (" ", fg),
                ("May 29 15:54 ", c("cyan")),
                ("openspec", c("cyan")),
            ],
            # d rwx r-x r-x  gmusa  staff      -  May 28 13:03 noctalia_color_scheme_manager
            [
                ("d", c("cyan")),
                (":", c("bright")),
                ("rwx", c("bright")),
                ("-", c("bright")),
                ("r-x", c("bright")),
                ("-", c("bright")),
                ("r-x", c("bright")),
                ("-", c("bright")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                ("  ", fg),
                ("-", c("bright")),
                (" ", fg),
                ("May 28 13:03 ", c("cyan")),
                ("noctalia_color_scheme_manager", c("cyan")),
            ],
            # - rw- r-- r--  gmusa  staff  2,2k  May 28 16:33 AGENTS.md
            [
                ("-", c("bright")),
                ("rw-", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                ("2,2k", c("green")),
                (" ", fg),
                ("May 28 16:33 ", c("cyan")),
                ("AGENTS.md", c("yellow")),
            ],
            # - rw- r-- r--  gmusa  staff   598  May 28 13:03 pyproject.toml
            [
                ("-", c("bright")),
                ("rw-", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                ("  ", fg),
                ("598", c("green")),
                (" ", fg),
                ("May 28 13:03 ", c("cyan")),
                ("pyproject.toml", c("yellow")),
            ],
            # - rw- r-- r--  gmusa  staff   466  May 28 16:01 pyrightconfig.json
            [
                ("-", c("bright")),
                ("rw-", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                ("  ", fg),
                ("466", c("green")),
                (" ", fg),
                ("May 28 16:01 ", c("cyan")),
                ("pyrightconfig.json", fg),
            ],
            # - rw- r-- r--  gmusa  staff   424  May 28 12:34 README.md
            [
                ("-", c("bright")),
                ("rw-", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                ("  ", fg),
                ("424", c("green")),
                (" ", fg),
                ("May 28 12:34 ", c("cyan")),
                ("README.md", c("yellow")),
            ],
            # - rw- r-- r--  gmusa  staff    86  May 28 13:01 main.py
            [
                ("-", c("bright")),
                ("rw-", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                ("r--", c("bright")),
                ("-", c("bright")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                ("  ", fg),
                (" 86", c("green")),
                (" ", fg),
                ("May 28 13:01 ", c("cyan")),
                ("main.py", fg),
            ],
            # - rwx r-x r-x  gmusa  staff   106  May 29 16:35 test.sh
            [
                ("-", c("bright")),
                ("rwx", c("green")),
                ("-", c("green")),
                ("r-x", c("green")),
                ("-", c("green")),
                ("r-x", c("green")),
                ("-", c("green")),
                (" ", fg),
                ("gmusa", c("yellow")),
                (" ", fg),
                ("staff", c("yellow")),
                (" ", fg),
                ("  ", fg),
                ("106", c("green")),
                (" ", fg),
                ("May 29 16:35 ", c("cyan")),
                ("test.sh", c("green")),
            ],
        ]

        for line in sample_lines:
            line_box = Gtk.Box()
            line_box.set_spacing(0)

            for text, color_key in line:
                lbl = Gtk.Label()
                lbl.set_text(text)
                lbl.set_halign(Gtk.Align.START)
                lbl.set_valign(Gtk.Align.CENTER)
                lbl.set_markup(f'<span color="{color_key}">{text}</span>')
                line_box.append(lbl)

            container.append(line_box)

        return container

    def cleanup(self) -> None:
        """Disconnect from reactive colors."""
        self.reactive_colors.disconnect(self._on_colors_changed)
