# Material Preview Reactive — Specification

## 1. Problem Statement

`MaterialPreview` muestra chips de colores Material Design, pero:

1. **Sin estados interactivos**: los chips no muestran estado hover
2. **Outline/shadow hardcodeados**: no son configurables
3. **Sin reactividad**: cuando `MaterialEditor` cambia un color, `MaterialPreview` no se actualiza
4. **ChipDrawingArea limitado**: no recibe colors de hover ni adapta al contexto (light/dark)

El resultado es un preview que no refleja la experiencia real del usuario.

## 2. User Experience

### Antes
- Preview estático que no responde a cambios del editor
- Chips sin feedback visual de hover
- No se puede previsualizar el efecto de outline/shadow

### Después
- Chips con hover fluido que usa `mHover`/`mOnHover`
- Outline/shadow configurables como propiedades del chip
- Preview se actualiza instantáneamente al cambiar colores en el editor
- Feedback visual inmediato de decisiones de diseño

## 3. Technical Approach

### 3.1 Signal-based Reactivity

Introducir un sistema de señales simple:

```python
class ColorsChangedCallback(Protocol):
    def on_colors_changed(self, colors: dict) -> None: ...

class ReactiveColors(GObject.Object):
    """Observable color state."""
    colors_changed: Signal
    
    def __init__(self, colors: dict) -> None: ...
    def update(self, key: str, value: str) -> None: ...
```

`MaterialEditor` crea `ReactiveColors`, lo pasa a `MaterialPreview`.
Cuando `ColorTile` cambia un color → `ReactiveColors.update()` → `MaterialPreview.on_colors_changed()`.

### 3.2 Enhanced ChipDrawingArea

```python
class ChipDrawingArea(Gtk.DrawingArea):
    """Chip with normal + hover states, optional outline/shadow."""
    
    def __init__(
        self,
        bg_color: str,          # Normal background
        fg_color: str,           # Normal foreground text
        hover_bg: str = None,   # Hover background (None = no hover effect)
        hover_fg: str = None,   # Hover foreground text
        outline_color: str = None,  # Border color (None = no border)
        shadow_color: str = None,  # Shadow color (None = no shadow)
        **kwargs
    ): ...
```

**Estados**:
- `NORMAL`: usa `bg_color`/`fg_color`
- `HOVER`: usa `hover_bg`/`hover_fg` si están definidos, si no oscurece/aclara `bg_color`

**Dibujo**:
1. Shadow (si está definido) — offset 3px
2. Background rect
3. Outline (si está definido) — 2px stroke
4. Text centered

**Hover detection**: conectar a `enter-notify-event` y `leave-notify-event` del widget.

### 3.3 ColorRow with Hover

```python
class ColorRow(Gtk.Box):
    """Row with 4 chips: (no O, no S), (O, no S), (no O, S), (O, S).
    
    Uses hover_bg/hover_fg for all chips.
    """
    
    def __init__(self, label: str, colors: dict, color_key: str, 
                 on_key: str, **kwargs): ...
```

### 3.4 Integration Flow

```
ThemeEditor.__init__()
  ├── ReactiveColors(colors)
  ├── MaterialEditor(colors)
  │     └── ColorTile(key, color)
  │           └── on_color_changed → reactive_colors.update()
  └── MaterialPreview(reactive_colors)
        └── on_colors_changed → queue_draw()
```

## 4. API

### 4.1 ChipDrawingArea Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `bg_color` | `str` | `"#808080"` | Normal background |
| `fg_color` | `str` | `"#ffffff"` | Normal foreground text |
| `hover_bg` | `str\|None` | `None` | Hover background |
| `hover_fg` | `str\|None` | `None` | Hover foreground |
| `outline_color` | `str\|None` | `None` | Border color |
| `shadow_color` | `str\|None` | `None` | Shadow color |
| `label` | `str` | `"Aa"` | Text to display |

### 4.2 Signals

| Signal | Payload | Emitter | Receiver |
|--------|---------|---------|----------|
| `colors-changed` | `dict` | `ReactiveColors` | `MaterialPreview` |
| `color-changed` | `key: str, value: str` | `ColorTile` | `MaterialEditor` |

## 5. Acceptance Criteria

- [ ] `ChipDrawingArea` dibuja correctamente en estado normal
- [ ] `ChipDrawingArea` responde a hover (enter/leave events) cambiando colores
- [ ] `ChipDrawingArea` soporta outline configurable (color, sin hardcoded)
- [ ] `ChipDrawingArea` soporta shadow configurable (color, sin hardcoded)
- [ ] `ChipDrawingArea` usa `hover_bg`/`hover_fg` cuando están definidos
- [ ] Cuando `hover_bg` es `None`, se calcula automáticamente desde `bg_color`
- [ ] `MaterialPreview` se actualiza cuando `MaterialEditor` cambia un color
- [ ] El flujo editor → reactive → preview funciona sin memory leaks
- [ ] El preview mantiene las 4 variantes (sin O/S, O, S, OS)
- [ ] Los chips mantienen proporción 60x40px con texto "Aa" centrado

## 6. Files to Change

| File | Change |
|------|--------|
| `ui/widgets/color_tile.py` | Añadir `hex_to_rgba`, mejorar `hex_to_rgb` |
| `ui/widgets/preview.py` | Reescribir `ChipDrawingArea` con hover y props |
| `ui/editors/material_editor.py` | Integrar `ReactiveColors`, conectar `ColorTile` |
| `ui/theme_editor.py` | Crear `ReactiveColors`, pasar a editor y preview |

## 7. Non-Goals

- No implementar undo/redo
- No guardar estado en disco
- No soportar múltiples temas simultáneamente
- No cambiar el layout visual existente (posición de chips, headers)
- No migrar TerminalPreview a sistema reactivo (out of scope)
