# Refactor Plan: Modular Architecture

## Goal

Convertir el mockup actual (`ui/mockup.py`) en módulos separados y reutilizables, con tests funcionales, preparando la estructura para el data layer.

---

## Module Structure

```
noctalia_color_scheme_manager/
├── __init__.py
├── main.py                    # Entry point
├── data/
│   ├── __init__.py
│   ├── theme_manager.py       # Filesystem operations (list, load, save, create)
│   ├── theme_model.py         # In-memory representation with signals
│   └── schema.py              # Validation against Noctalia schema
├── ui/
│   ├── __init__.py
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── color_tile.py      # ColorTile, ColorSwatch, ContrastTile
│   │   └── preview.py         # MaterialPreviewFrame, TerminalPreviewFrame
│   ├── editors/
│   │   ├── __init__.py
│   │   ├── material_editor.py # MaterialEditor (grid layout)
│   │   └── terminal_editor.py # TerminalEditor (grid layout)
│   ├── main_window.py         # MainWindow (sidebar + theme list + new theme)
│   ├── theme_editor.py        # ThemeEditor (tabs Dark/Light + actions)
│   ├── variant_page.py        # VariantPage (Material + Terminal cards)
│   ├── app.py                 # App (Adw.Application + window setup)
│   ├── mockup.py              # Original (mantener para referencia)
│   └── mockup_preview.py      # Integrado con módulos nuevos
└── ui.py                      # Re-exports for convenience
```

---

## Phase 1: Widgets ✅

### `widgets/color_tile.py` ✅
- `ColorSwatch` — DrawingArea que pinta un color sólido
- `ColorTile` — label + hex entry + ColorButton
  - params: `label`, `color`, `show_label`
- `ContrastTile` — para editor de material (bg + fg en un row)
  - params: `label`, `bg_color`, `fg_color`
- `hex_to_rgb()`, `hex_to_rgba()` utilities

### `widgets/preview.py` ✅
- `MaterialPreview` — frame con Primary/Secondary buttons simulados
- `TerminalPreview` — frame con prompt/output simulado

### Tests ✅
```python
# tests/test_widgets.py
class TestColorSwatch:
    - test_creates_with_color
    - test_default_size
    - test_custom_size

class TestColorTile:
    - test_creates_with_label_and_color
    - test_show_label_false_hides_label
    - test_hex_entry_populated

class TestContrastTile:
    - test_creates_with_bg_and_fg
    - test_both_pickers_created
```

---

## Phase 2: Editors

### `editors/material_editor.py` ✅
- `MaterialEditor(Gtk.Box)` — grid layout
  - Header: Background | Foreground
  - Rows: Primary, Secondary, Tertiary, Error, Surface, Surface Variant, Hover
  - Separator row
  - Effects section: Outline, Shadow
- Usa `ColorTile` para cada color

### `editors/terminal_editor.py` ✅
- `TerminalEditor(Gtk.Box)` — grid layout
  - Header: Normal | Bright (con labels de colores en col 0)
  - Rows: black, red, green, yellow, blue, magenta, cyan, white
  - Separator row
  - Special section: foreground, background, cursor, selectionFg, selectionBg

### Tests ✅
```python
# tests/test_editors.py
class TestMaterialEditor:
    - test_creates_with_colors_dict
    - test_all_material_pairs_rendered
    - test_separator_row_exists
    - test_effects_section_exists

class TestTerminalEditor:
    - test_creates_with_terminal_colors
    - test_all_8_color_rows_rendered
    - test_special_section_exists
    - test_normal_and_bright_columns
```

---

## Phase 3: UI Components

### `main_window.py`
- `Sidebar(Gtk.Box)` — lista de themes + crear nuevo
- `MainWindow(Adw.Bin)` — sidebar + content

### `variant_page.py`
- `VariantPage(Gtk.Box)`
  - Material card con título + editor + preview
  - Terminal card con título + editor + preview
  - Ambos en columna

### `theme_editor.py`
- `ThemeEditor(Gtk.Box)`
  - Título (nombre del theme)
  - `Gtk.Stack` + `Gtk.StackSwitcher` para Dark/Light tabs
  - Action buttons: Save, Export, Backup, Check Contrast

### `app.py`
- `App(Adw.Application)` — setup con `activate` signal
- `create_window()` — factory para ventana principal

---

## Phase 3.5: Mockup Preview (Integration)

### `ui/mockup_preview.py` ✨ NUEVO
- Integrado con módulos nuevos (widgets + editors)
- Reemplaza el uso de clases inline por imports
- Demo funcional con datos Monokai hardcodeados
- Verifica que todos los componentes funcionen juntos

```python
# tests/test_mockup_preview.py
class TestMockupPreview:
    - test_imports_all_modules
    - test_variant_page_creates_correctly
    - test_theme_editor_has_dark_light_tabs
    - test_main_window_has_sidebar
    - test_app_creates_window
```

---

## Phase 4: Data Layer

### `data/theme_manager.py`
```python
class ThemeManager:
    THEMES_DIR = Path("~/.config/noctalia/colorschemes")

    def list_themes(self) -> list[str]
    def load_theme(self, name: str) -> ThemeModel
    def save_theme(self, name: str, theme: ThemeModel) -> None
    def create_theme(self, name: str, template: str = "monokai") -> ThemeModel
    def delete_theme(self, name: str) -> None
    def theme_exists(self, name: str) -> bool
```

### `data/theme_model.py`
```python
@dataclass
class VariantColors:
    """Material tokens + Terminal colors for one variant."""
    # Material
    mPrimary: str
    mOnPrimary: str
    mSecondary: str
    mOnSecondary: str
    mTertiary: str
    mOnTertiary: str
    mError: str
    mOnError: str
    mSurface: str
    mOnSurface: str
    mSurfaceVariant: str
    mOnSurfaceVariant: str
    mOutline: str
    mShadow: str
    mHover: str
    mOnHover: str
    # Terminal
    terminal: TerminalColors

@dataclass
class TerminalColors:
    foreground: str
    background: str
    normal: dict[str, str]   # 8 colors
    bright: dict[str, str]  # 8 colors
    cursor: str
    cursorText: str
    selectionFg: str
    selectionBg: str

@dataclass
class ThemeModel:
    name: str
    dark: VariantColors
    light: VariantColors
```

### `data/schema.py`
- `validate_theme(data: dict) -> bool` — valida estructura del JSON
- `validate_color(hex: str) -> bool` — valida formato hex
- `DEFAULT_THEME` — template monokai para nuevos themes

### Tests ✅
```python
# tests/test_theme_manager.py
class TestThemeManager:
    - test_list_themes_returns_list
    - test_load_theme_parses_json
    - test_save_theme_writes_file
    - test_create_theme_from_template
    - test_delete_theme_removes_file
    - test_theme_exists_check

class TestSchema:
    - test_validate_theme_accepts_valid
    - test_validate_theme_rejects_invalid
    - test_validate_color_accepts_hex
    - test_validate_color_rejects_invalid
```

---

## Integration Steps

1. **Tests Phase 1-2** ← AHORA
2. **Phase 3** — UI components (main_window, variant_page, theme_editor, app)
3. **Phase 3.5** — mockup_preview integrado
4. **Phase 4** — data layer con tests
5. **Conectar data → UI** con signals/properties

---

## Testing Strategy

- **Widgets/Editors**: tests funcionales que instancian GTK widgets y verifican estructura
- **Data layer**: tests con tmpfs para filesystem operations
- **UI components**: tests de integración verificando composición
- Usar `pytest` con `pytest-gtk` o tests manuales GTK

---

## Next Session Checklist

- [x] Crear estructura de directorios
- [x] Implementar widgets (color_tile, preview)
- [x] Implementar editors (material, terminal)
- [ ] Tests para widgets (color_tile, preview)
- [ ] Tests para editors (material, terminal)
- [ ] Implementar UI components (main_window, variant_page, theme_editor, app)
- [ ] Phase 3.5: mockup_preview.py integrado
- [ ] Implementar data layer (theme_manager, theme_model, schema)
- [ ] Tests para data layer
- [ ] Conectar data → UI