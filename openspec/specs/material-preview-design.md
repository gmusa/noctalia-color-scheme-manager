# Material Preview Reactive — Design

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         ThemeEditor                             │
│  ┌───────────────┐    ┌──────────────────────────────────────┐  │
│  │ ReactiveColors │    │        MaterialEditor               │  │
│  │                │    │  ┌────────────────────────────────┐  │  │
│  │  _colors: dict │    │  │         ColorTile             │  │  │
│  │  ───────────── │◄───┤  │   [bg] [fg] [picker] [hex]   │──┼──┼──│
│  │  update(key,v) │    │  └────────────────────────────────┘  │  │
│  │  colors_changed│    │        ▲         ▲                   │  │
│  │    (signal)    │    │        │         │ on_color_changed │  │
│  └───────┬───────┘    └────────┼─────────┼───────────────────┘  │
│          │                     │         │                      │
│          │ colors_changed      │         │                      │
│          ▼                     │         │                      │
│  ┌───────────────┐             │         │                      │
│  │MaterialPreview│◄────────────┴─────────┘                      │
│  │               │                                              │
│  │  ColorRow ×6   │                                              │
│  │    └──Chip     │                                              │
│  │      (hover)   │                                              │
│  └───────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Signal Flow

```
ColorTile.on_color_changed(key, value)
    ↓
ReactiveColors.update(key, value)
    ↓
ReactiveColors.emit('colors-changed', colors_copy)
    ↓
MaterialPreview.on_colors_changed(colors)
    ↓
MaterialPreview.queue_draw()
    ↓
All ChipDrawingArea children redraw with new colors
```

## 2. ReactiveColors — Class Design

```python
from gi.repository import GObject


class ReactiveColors(GObject.GObject):
    """Observable dictionary of colors with signal emission on change."""
    
    __gsignals__ = {
        'colors-changed': (
            GObject.SignalFlags.RUN_LAST,  # type
            None,                          # return type
            (dict,)                        # param types
        ),
    }
    
    def __init__(self, colors: dict) -> None:
        super().__init__()
        self._colors = dict(colors)  # Copy to avoid external mutation
    
    def get(self, key: str, default: str = "#808080") -> str:
        return self._colors.get(key, default)
    
    def get_all(self) -> dict:
        """Return a copy of the colors dict."""
        return dict(self._colors)
    
    def update(self, key: str, value: str) -> None:
        """Update a single color and emit signal."""
        if key in self._colors and self._colors[key] == value:
            return  # No-op if value unchanged
        self._colors[key] = value
        self.emit('colors-changed', self.get_all())
```

**Key decisions**:
- `_colors` es privado, no se expone directamente
- `get_all()` retorna copia para evitar side-effects
- `update()` compara valor previo para evitar emission innecesaria
- Signal `colors-changed` pasa una copia para thread-safety

## 3. ChipDrawingArea — Enhanced Design

### 3.1 Class Definition

```python
class ChipDrawingArea(Gtk.DrawingArea):
    """Custom DrawingArea for a color chip with hover, outline, shadow."""
    
    # GTK4: DrawingArea needs has_window=True for events
    __gtype_name__ = 'ChipDrawingArea'
    
    def __init__(
        self,
        bg_color: str = "#808080",
        fg_color: str = "#ffffff",
        hover_bg: str | None = None,
        hover_fg: str | None = None,
        outline_color: str | None = None,
        shadow_color: str | None = None,
        label: str = "Aa",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.set_has_window(True)  # Required for hover events
        
        # Store properties
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.outline_color = outline_color
        self.shadow_color = shadow_color
        self.label = label
        
        # State
        self._is_hovering = False
        
        # Size
        self.set_size_request(60, 40)
        
        # Draw callback
        self.set_draw_func(self._draw)
        
        # Hover events
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)
    
    def set_bg_color(self, color: str) -> None:
        self.bg_color = color
        self.queue_draw()
    
    def set_fg_color(self, color: str) -> None:
        self.fg_color = color
        self.queue_draw()
    
    def set_hover_colors(self, bg: str | None, fg: str | None) -> None:
        self.hover_bg = bg
        self.hover_fg = fg
        self.queue_draw()
    
    def set_outline(self, color: str | None) -> None:
        self.outline_color = color
        self.queue_draw()
    
    def set_shadow(self, color: str | None) -> None:
        self.shadow_color = color
        self.queue_draw()
```

### 3.2 Hover Detection

```python
def _on_enter(self, widget, event) -> bool:
    self._is_hovering = True
    self.queue_draw()
    return Gdk.EVENT_STOP

def _on_leave(self, widget, event) -> bool:
    self._is_hovering = False
    self.queue_draw()
    return Gdk.EVENT_STOP
```

### 3.3 Draw Logic

```python
def _get_effective_colors(self) -> tuple[str, str]:
    """Return (bg, fg) based on hover state."""
    if self._is_hovering:
        bg = self.hover_bg if self.hover_bg else self._darken(self.bg_color)
        fg = self.hover_fg if self.hover_fg else self.fg_color
        return bg, fg
    return self.bg_color, self.fg_color

@staticmethod
def _darken(hex_color: str, amount: float = 0.1) -> str:
    """Darken a hex color by amount (0.0-1.0)."""
    r, g, b = hex_to_rgb(hex_color)
    r = max(0.0, r - amount)
    g = max(0.0, g - amount)
    b = max(0.0, b - amount)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def _draw(self, area, cr, w, h, data=None):
    bg, fg = self._get_effective_colors()
    
    # Shadow (if defined)
    if self.shadow_color:
        sr, sg, sb = hex_to_rgb(self.shadow_color)
        cr.set_source_rgba(sr, sg, sb, 0.35)  # Fixed opacity
        cr.rectangle(3, 3, w - 3, h - 3)
        cr.fill()
    
    # Main background
    r, g, b = hex_to_rgb(bg)
    cr.set_source_rgb(r, g, b)
    cr.rectangle(0, 0, w, h)
    cr.fill()
    
    # Outline (if defined)
    if self.outline_color:
        or_, og, ob = hex_to_rgb(self.outline_color)
        cr.set_source_rgba(or_, og, ob, 0.7)
        cr.set_line_width(2)
        cr.rectangle(1, 1, w - 2, h - 2)
        cr.stroke()
    
    # Text
    r2, g2, b2 = hex_to_rgb(fg)
    cr.set_source_rgb(r2, g2, b2)
    cr.select_font_face("Sans", 0, 0)
    cr.set_font_size(13)
    extents = cr.text_extents(self.label)
    x = (w - extents.width) / 2
    y = (h + extents.height) / 2 - 2
    cr.move_to(x, y)
    cr.show_text(self.label)
```

### 3.4 Hover State Machine

```
┌──────────┐  enter-notify  ┌──────────┐
│  NORMAL  │──────────────►│  HOVER   │
│          │◄──────────────│          │
└──────────┘  leave-notify └──────────┘
```

- NORMAL → HOVER: cursor enters widget
- HOVER → NORMAL: cursor leaves widget
- Redraw triggered on every transition

## 4. ColorRow Integration

### 4.1 Constructor

```python
class ColorRow(Gtk.Box):
    def __init__(
        self,
        label: str,
        colors: ReactiveColors,
        color_key: str,
        on_key: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(4)
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.CENTER)
        
        self.reactive_colors = colors
        self.color_key = color_key
        self.on_key = on_key
        
        # Connect to reactive colors
        colors.connect('colors-changed', self._on_colors_changed)
        
        # Label
        self._build_label(label)
        
        # 4 chips: (no O, no S), (O, no S), (no O, S), (O, S)
        outline_key = "mOutline"
        shadow_key = "mShadow"
        hover_bg = colors.get('mHover')
        hover_fg = colors.get('mOnHover')
        
        self.chips = []
        for has_outline, has_shadow in [
            (False, False),
            (True, False),
            (False, True),
            (True, True)
        ]:
            chip = self._create_chip(
                colors, outline_key, shadow_key, 
                hover_bg, hover_fg,
                has_outline, has_shadow
            )
            self.chips.append(chip)
            self.append(chip)
    
    def _on_colors_changed(self, reactive, colors):
        self._update_chips(colors)
    
    def _update_chips(self, colors):
        bg = colors.get(self.color_key)
        fg = colors.get(self.on_key)
        outline = colors.get("mOutline")
        shadow = colors.get("mShadow")
        hover_bg = colors.get("mHover")
        hover_fg = colors.get("mOnHover")
        
        for i, (has_outline, has_shadow) in enumerate([
            (False, False), (True, False), (False, True), (True, True)
        ]):
            chip = self.chips[i]
            chip.bg_color = bg
            chip.fg_color = fg
            chip.outline_color = outline if has_outline else None
            chip.shadow_color = shadow if has_shadow else None
            chip.hover_bg = hover_bg
            chip.hover_fg = hover_fg
            chip.queue_draw()
```

## 5. MaterialPreview Integration

### 5.1 Constructor

```python
class MaterialPreview(Gtk.Frame):
    def __init__(self, reactive_colors: ReactiveColors, **kwargs):
        super().__init__(**kwargs)
        self.reactive_colors = reactive_colors
        
        # Connect signal
        reactive_colors.connect('colors-changed', self._on_colors_changed)
        
        # ... rest of UI setup ...
```

### 5.2 Signal Handler

```python
def _on_colors_changed(self, reactive, colors):
    """Update all rows when colors change."""
    for row in self.rows:
        row._update_chips(colors)
```

## 6. MaterialEditor Integration

### 6.1 ColorTile Enhancement

```python
class ColorTile(Gtk.Box):
    def __init__(self, label: str, color_key: str, 
                 reactive_colors: ReactiveColors | None = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.color_key = color_key
        self.reactive_colors = reactive_colors
        
        # ... UI setup ...
        
        # Connect signals
        self.hex_entry.connect("changed", self._on_hex_changed)
        self.color_btn.connect("color-set", self._on_color_set)
    
    def _on_hex_changed(self, entry):
        value = entry.get_text()
        if self._validate_hex(value):
            self._emit_change(value)
    
    def _on_color_set(self, btn):
        rgba = btn.get_rgba()
        value = f"#{int(rgba.red*255):02x}{int(rgba.green*255):02x}{int(rgba.blue*255):02x}"
        self.hex_entry.set_text(value)
        self._emit_change(value)
    
    def _emit_change(self, value: str):
        if self.reactive_colors:
            self.reactive_colors.update(self.color_key, value)
```

### 6.2 Editor Constructor

```python
class MaterialEditor(Gtk.Box):
    def __init__(self, reactive_colors: ReactiveColors, **kwargs):
        super().__init__(**kwargs)
        self.reactive_colors = reactive_colors
        
        # Pass reactive_colors to each ColorTile
        for label, bg_key, fg_key in MATERIAL_PAIRS:
            bg_tile = ColorTile(bg_key, bg_key, reactive_colors, ...)
            fg_tile = ColorTile(fg_key, fg_key, reactive_colors, ...)
            # ...
```

## 7. ThemeEditor Orchestration

```python
class ThemeEditor(Gtk.Box):
    def __init__(self, theme_name, dark_colors, light_colors, **kwargs):
        super().__init__(**kwargs)
        
        # Create reactive color stores
        self.dark_reactive = ReactiveColors(dark_colors)
        self.light_reactive = ReactiveColors(light_colors)
        
        # Material editor + preview share same reactive instance
        mat_editor = MaterialEditor(self.dark_reactive)
        mat_preview = MaterialPreview(self.dark_reactive)
        
        # When tab changes, swap reactive instance
        # (handled by switching which reactive is connected)
```

## 8. Tradeoffs

### Decision A: ReactiveColors vs direct parent-child coupling
**Chosen**: ReactiveColors with signals
- **Pros**: Decoupled, testable, extensible
- **Cons**: More code, GObject overhead

**Alternative**: Parent passes callback to editor
- **Pros**: Simpler, no GObject needed
- **Cons**: Tight coupling, harder to add more consumers

### Decision B: Shadow opacity hardcoded vs configurable
**Chosen**: Shadow color configurable, opacity fixed at 0.35
- **Pros**: Simpler API (one color param), consistent shadow look
- **Cons**: Less flexibility

**Alternative**: Both color and opacity configurable
- **Pros**: Full control
- **Cons**: API bloat for marginal benefit

### Decision C: Auto-darken on hover vs explicit hover colors
**Chosen**: Use explicit `hover_bg` if provided, else auto-darken
- **Pros**: Sensible default, explicit override when needed
- **Cons**: Auto-darken may not match Material spec exactly

### Decision D: Copy on signal vs reference
**Chosen**: Signal passes dict copy
- **Pros**: Thread-safe, consumer can't mutate state
- **Cons**: Memory overhead for large dicts

## 9. File Changes Summary

| File | Add | Modify | Delete |
|------|-----|--------|--------|
| `ui/widgets/color_tile.py` | `_darken()` | `hex_to_rgb()` add 3-digit support | — |
| `ui/widgets/preview.py` | `ReactiveColors`, `ChipDrawingArea` rewrite | `ColorRow`, `MaterialPreview` | old `ChipDrawingArea` |
| `ui/editors/material_editor.py` | — | `ColorTile` signal, `MaterialEditor` accepts `ReactiveColors` | — |
| `ui/theme_editor.py` | `ReactiveColors` creation | Pass to editor/preview | — |

## 10. Estimated Lines of Change

- `color_tile.py`: ~30 lines
- `preview.py`: ~200 lines (rewrite)
- `material_editor.py`: ~50 lines
- `theme_editor.py`: ~20 lines

**Total**: ~300 lines — dentro del budget de 400 para single PR.
