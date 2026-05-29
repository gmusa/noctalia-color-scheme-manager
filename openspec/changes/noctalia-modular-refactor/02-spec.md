# Spec: Noctalia Modular Refactor

## 1. Module Structure (Target)

```
noctalia_color_scheme_manager/
├── __init__.py
├── main.py                    # Entry point → App()
├── data/
│   ├── __init__.py
│   ├── theme_manager.py       # Filesystem operations
│   ├── theme_model.py         # Dataclasses + signals
│   └── schema.py              # Validation
├── ui/
│   ├── __init__.py            # Re-exports for convenience
│   ├── app.py                 # Adw.Application + window factory
│   ├── main_window.py         # Sidebar + content layout
│   ├── theme_editor.py        # ThemeEditor con tabs Dark/Light
│   ├── variant_page.py        # VariantPage con Material + Terminal
│   ├── mockup.py              # Original (deprecado, mantener ref)
│   └── mockup_preview.py      # Demo funcional con módulos nuevos
└── ui/widgets/
│   ├── __init__.py
│   ├── color_tile.py
│   └── preview.py
└── ui/editors/
    ├── __init__.py
    ├── material_editor.py
    └── terminal_editor.py
```

## 2. Acceptance Criteria

### 2.1 Widgets (`ui/widgets/`)

- [ ] `ColorSwatch` dibuja un cuadrado del color dado
- [ ] `ColorTile` muestra label + hex entry + ColorButton
- [ ] `ContrastTile` muestra label + bg tile + fg tile
- [ ] `MaterialPreview` renderiza frame con Primary/Secondary buttons
- [ ] `TerminalPreview` renderiza frame con prompt/output simulado
- [ ] Todos los widgets tienen `set_color()` para actualización reactiva

### 2.2 Editors (`ui/editors/`)

- [ ] `MaterialEditor` renderiza grid con 7 pairs + Effects + Outline/Shadow
- [ ] `TerminalEditor` renderiza 16 colores normals + Specials
- [ ] Headers "Background" y "Foreground" en MaterialEditor
- [ ] Headers "Normal" y "Bright" en TerminalEditor
- [ ] Separators visuales entre secciones

### 2.3 UI Components (`ui/`)

- [ ] `variant_page.py`:
  - Material card con título + editor + preview
  - Terminal card con título + editor + preview
  - Cards en columna vertical

- [ ] `theme_editor.py`:
  - Título con nombre del theme
  - StackSwitcher para Dark/Light tabs
  - Botones: Save, Export, Backup, Check Contrast

- [ ] `main_window.py`:
  - Sidebar con lista de themes (ToggleButtons)
  - Botón "New theme" con entry
  - Content area con editor

- [ ] `app.py`:
  - Adw.Application con activate signal
  - Window factory
  - Título "Noctalia Color Scheme Manager"
  - Tamaño default 1100x750

### 2.4 Mockup Preview (`ui/mockup_preview.py`)

- [ ] Demo funcional con Monokai dark/light hardcodeados
- [ ] Usa imports de `ui/widgets/` y `ui/editors/`
- [ ] Ejecutable como `python -m noctalia_color_scheme_manager.ui.mockup_preview`

### 2.5 Data Layer (`data/`)

- [ ] `ThemeModel` dataclass con:
  - `name: str`
  - `dark: VariantColors`
  - `light: VariantColors`
  - `VariantColors` con todos los tokens Material + Terminal
  - Signals para cambio de colores

- [ ] `ThemeManager`:
  - `THEMES_DIR = ~/.config/noctalia/colorschemes`
  - `list_themes() -> list[str]`
  - `load_theme(name: str) -> ThemeModel`
  - `save_theme(theme: ThemeModel) -> None`
  - `create_theme(name: str, template: str = "monokai") -> ThemeModel`
  - `delete_theme(name: str) -> None`
  - `theme_exists(name: str) -> bool`

- [ ] `Schema`:
  - `validate_theme(data: dict) -> bool`
  - `validate_color(hex: str) -> bool`
  - `DEFAULT_THEME` template Monokai

### 2.6 Integration

- [ ] `main.py` inicia `App().run()` en vez del stub actual
- [ ] `ui/__init__.py` re-exports públicos de todos los módulos

## 3. Test Strategy

### 3.1 GTK Functional Tests (pytest-lax)

```python
# tests/test_widgets.py
class TestColorSwatch:
    def test_creates_with_color():
        swatch = ColorSwatch("#ff0000")
        assert swatch._color == "#ff0000"

    def test_default_size():
        swatch = ColorSwatch("#000000")
        # Check size_request

    def test_set_color_updates():
        swatch = ColorSwatch("#000000")
        swatch.set_color("#00ff00")
        assert swatch._color == "#00ff00"
```

### 3.2 Data Layer Tests (tmpfs)

```python
# tests/test_theme_manager.py
class TestThemeManager:
    def test_list_themes_returns_list(tmp_path, monkeypatch):
        # Mock THEMES_DIR to tmp_path
        # Create sample themes
        # Assert list_themes() returns them

    def test_save_load_roundtrip(tmp_path, monkeypatch):
        # Save theme → load → assert equality
```

## 4. Dependencies

- `pygobject>=3.48` (GTK4)
- `pyyaml>=6.0` (data layer)
- `pytest>=8.0` (testing)
- `pytest-lax` o `pytest-xvfb` (GTK without display)

## 5. Out of Scope (v2)

- Señales bidireccionales data ↔ UI
- Editor real con change listeners
- Import/export a otros formatos
- Tema claro/oscuro dinámico de la app misma
