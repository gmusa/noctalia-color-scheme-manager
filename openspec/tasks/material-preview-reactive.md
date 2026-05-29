# Material Preview Reactive — Tasks

## Implementation Order

```
1. [ ] Utilities: hex_to_rgb improvements + _darken
2. [ ] Core: ReactiveColors GObject class
3. [ ] Widget: Enhanced ChipDrawingArea with hover
4. [ ] Widget: Update ColorRow to use ReactiveColors
5. [ ] Widget: Update MaterialPreview to use ReactiveColors
6. [ ] Editor: Enhance ColorTile with signal emission
7. [ ] Editor: Update MaterialEditor to accept ReactiveColors
8. [ ] Orchestrator: Update ThemeEditor to create and pass ReactiveColors
9. [ ] Test: Manual verification in app
```

## Task Details

### Task 1: Utilities — hex_to_rgb + _darken

**File**: `ui/widgets/color_tile.py`

**Changes**:
1. `hex_to_rgb()` already handles 3-digit shorthand — verify it's correct
2. Add `_darken(hex_color: str, amount: float = 0.1) -> str` static method

**Acceptance**: `_darken("#ff0000")` returns a darker red, `hex_to_rgb("#f00")` works.

---

### Task 2: Core — ReactiveColors

**File**: `ui/widgets/preview.py` (add at top)

**Implementation**:
```python
class ReactiveColors(GObject.GObject):
    """Observable dictionary of colors with signal emission on change."""
    
    __gsignals__ = {
        'colors-changed': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (dict,)
        ),
    }
    
    def __init__(self, colors: dict) -> None:
        super().__init__()
        self._colors = dict(colors)
    
    def get(self, key: str, default: str = "#808080") -> str:
        return self._colors.get(key, default)
    
    def get_all(self) -> dict:
        return dict(self._colors)
    
    def update(self, key: str, value: str) -> None:
        if key in self._colors and self._colors[key] == value:
            return
        self._colors[key] = value
        self.emit('colors-changed', self.get_all())
```

**Acceptance**: `ReactiveColors` emits `colors-changed` when `update()` is called with new value.

---

### Task 3: Widget — Enhanced ChipDrawingArea

**File**: `ui/widgets/preview.py`

**Replace existing class with**:
- Properties: `bg_color`, `fg_color`, `hover_bg`, `hover_fg`, `outline_color`, `shadow_color`, `label`
- `_is_hovering: bool` state
- `set_has_window(True)` in `__init__`
- Hover event handlers `_on_enter`, `_on_leave`
- `_get_effective_colors()` method with auto-darken fallback
- Updated `_draw()` using all properties

**Acceptance**:
- [ ] Chip renders with background/fg_color
- [ ] Hover changes colors smoothly
- [ ] Outline renders when `outline_color` is set
- [ ] Shadow renders when `shadow_color` is set
- [ ] Auto-darken works when `hover_bg` is `None`

---

### Task 4: Widget — Update ColorRow

**File**: `ui/widgets/preview.py`

**Changes**:
1. Constructor accepts `ReactiveColors` instead of `dict`
2. Connect to `colors-changed` signal
3. Create 4 chips with `hover_bg`/`hover_fg` from reactive colors
4. Add `_update_chips(colors)` method

**Acceptance**:
- [ ] ColorRow renders 4 chips correctly
- [ ] `_on_colors_changed` updates all 4 chips

---

### Task 5: Widget — Update MaterialPreview

**File**: `ui/widgets/preview.py`

**Changes**:
1. Constructor accepts `ReactiveColors` instead of `dict`
2. Connect to `colors-changed` signal
3. Pass `ReactiveColors` to each `ColorRow`
4. Add `_on_colors_changed` handler

**Acceptance**:
- [ ] MaterialPreview renders with ReactiveColors
- [ ] Signal handler triggers redraw

---

### Task 6: Editor — Enhance ColorTile

**File**: `ui/widgets/color_tile.py`

**Changes**:
```python
class ColorTile(Gtk.Box):
    def __init__(self, label: str, color_key: str, 
                 reactive_colors: ReactiveColors | None = None,
                 **kwargs):
        # ... existing init ...
        self.color_key = color_key
        self.reactive_colors = reactive_colors
        
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
    
    @staticmethod
    def _validate_hex(value: str) -> bool:
        return bool(re.match(r'^#[0-9a-fA-F]{6}$', value))
```

**Acceptance**:
- [ ] Hex entry change triggers `reactive_colors.update()`
- [ ] Color picker change triggers `reactive_colors.update()`

---

### Task 7: Editor — Update MaterialEditor

**File**: `ui/editors/material_editor.py`

**Changes**:
1. Constructor accepts `reactive_colors: ReactiveColors` instead of `colors: dict`
2. Pass `reactive_colors` to each `ColorTile`
3. Remove direct `colors.get()` calls, use `reactive_colors.get()` if needed

**Acceptance**:
- [ ] MaterialEditor creates tiles that emit signals

---

### Task 8: Orchestrator — Update ThemeEditor

**File**: `ui/theme_editor.py`

**Changes**:
1. Import `ReactiveColors` from `.widgets.preview`
2. Create `ReactiveColors` instances in `__init__`
3. Pass `ReactiveColors` to `MaterialEditor` and `MaterialPreview`

```python
from .widgets.preview import MaterialPreview, TerminalPreview, ReactiveColors

# In __init__:
self.dark_reactive = ReactiveColors(dark_colors)
self.light_reactive = ReactiveColors(light_colors)

# In _build_card:
editor = MaterialEditor(self.dark_reactive)
preview = MaterialPreview(self.dark_reactive)
```

**Acceptance**:
- [ ] App runs without errors
- [ ] Editor and preview share same ReactiveColors instance

---

### Task 9: Test — Manual Verification

**Actions**:
1. Run: `python -m noctalia_color_scheme_manager.main`
2. Hover over a chip → should change color
3. Edit hex value in MaterialEditor → preview should update
4. Change color via picker → preview should update
5. Toggle Dark/Light tab → should show correct colors

**Expected**:
- Hover visible on chips
- Preview updates within 100ms of editor change
- No console errors

---

## Dependency Graph

```
Task 1 (utilities)
    ↓
Task 2 (ReactiveColors)
    ↓        ↓
Task 3    Task 6
(Chip)    (ColorTile)
    ↓        ↓
Task 4    Task 7
(ColorRow) (MaterialEditor)
    ↓        ↓
Task 5 ───────
(MaterialPreview)
    ↓
Task 8 (ThemeEditor)
    ↓
Task 9 (test)
```

## Notes

- Task 1 and 2 are independent of widget/editor changes
- Task 3 depends on Task 1 (uses `_darken`)
- Tasks 4-5 depend on Tasks 2-3
- Tasks 6-7 depend on Task 2
- Task 8 depends on Tasks 5 and 7
- Task 9 depends on all
