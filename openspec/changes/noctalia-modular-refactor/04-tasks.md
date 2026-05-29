# Tasks: Noctalia Modular Refactor

## Overview

- **Total estimated tasks**: 15
- **Estimated review workload**: ~400 líneas de diff (bajo riesgo)

## Task Breakdown

### Phase 3.5: Mockup Preview (Integration)

#### T-01: Crear `ui/variant_page.py`
- Extraer VariantPage de `mockup_new.py`
- Usar imports de `widgets/` y `editors/`
- Tests: instanciación, cards rendered

#### T-02: Crear `ui/theme_editor.py`
- Extraer ThemeEditor de `mockup_new.py`
- Usar VariantPage del módulo nuevo
- Tests: tabs Dark/Light, action buttons

#### T-03: Crear `ui/main_window.py`
- Extraer MainWindow de `mockup_new.py`
- Usar ThemeEditor del módulo nuevo
- Tests: sidebar existe, content area existe

#### T-04: Crear `ui/app.py`
- Extraer App de `mockup_new.py`
- Tests: App crea window correctamente

#### T-05: Crear `ui/mockup_preview.py`
- Demo funcional con datos Monokai hardcodeados
- Verificar que usa todos los módulos nuevos
- Ejecutable como módulo: `python -m nctheme.ui.mockup_preview`

#### T-06: Deprecar `ui/mockup.py`
- Mover a `ui/deprecated/mockup.py`
- Agregar comment `# DEPRECATED: Use mockup_preview.py`
- NO eliminar hasta que mockup_preview esté verificado

#### T-07: Actualizar `ui/__init__.py`
- Re-exports públicos:
  ```python
  from .app import App
  from .main_window import MainWindow
  from .theme_editor import ThemeEditor
  from .variant_page import VariantPage
  ```

#### T-08: Actualizar `main.py`
- Importar y ejecutar App
- Remover el stub "Hello from..."
- Tests: `python -m noctalia_color_scheme_manager.main` inicia la GUI

---

### Phase 4: Data Layer

#### T-09: Crear `data/theme_model.py`
- TerminalColors dataclass
- VariantColors dataclass  
- ThemeModel dataclass con signal callbacks
- Tests: instanciación, callbacks invocados

#### T-10: Crear `data/schema.py`
- `validate_theme(data: dict) -> bool`
- `validate_color(hex: str) -> bool`
- `DEFAULT_THEME` template Monokai
- Tests: validaciones correctas, rejection de invalid

#### T-11: Crear `data/theme_manager.py`
- ThemeManager class
- THEMES_DIR = ~/.config/noctalia/colorschemes
- Métodos: list_themes, load_theme, save_theme, create_theme, delete_theme, theme_exists
- Tests con tmpfs: roundtrip save/load

#### T-12: Actualizar `data/__init__.py`
- Re-exports:
  ```python
  from .theme_manager import ThemeManager
  from .theme_model import ThemeModel, VariantColors, TerminalColors
  from .schema import Schema
  ```

---

### Testing Setup

#### T-13: Configurar pytest
- Agregar `pytest>=8.0` a pyproject.toml
- Crear `tests/` directory
- pytest fixture para Gtk.Application
- pytest fixture para tmpfs ThemeManager

#### T-14: Tests para Widgets
```
tests/
├── __init__.py
├── test_widgets/
│   ├── __init__.py
│   ├── test_color_tile.py
│   └── test_preview.py
├── test_editors/
│   ├── __init__.py
│   ├── test_material_editor.py
│   └── test_terminal_editor.py
├── test_ui/
│   ├── __init__.py
│   ├── test_variant_page.py
│   ├── test_theme_editor.py
│   └── test_main_window.py
└── test_data/
    ├── __init__.py
    ├── test_theme_model.py
    ├── test_schema.py
    └── test_theme_manager.py
```

#### T-15: Tests para Data Layer
- theme_model: instanciación, signal callbacks
- schema: validate_theme, validate_color
- theme_manager: list, save, load, delete con tmpfs

---

## Dependency Graph

```
T-01 (variant_page) ─┬─→ usa widgets, editors
T-02 (theme_editor) ─┴─→ usa variant_page
T-03 (main_window) ──→ usa theme_editor
T-04 (app) ──────────→ usa main_window
T-05 (mockup_preview) ─┴─→ usa todos los módulos
T-06 (deprecate) ──────→ necesita T-05
T-07 (ui init) ────────→ necesita T-01 a T-04
T-08 (main.py) ─────────→ necesita T-04
─────────────────────────────
T-09 (theme_model) ────→ sin dependencias
T-10 (schema) ─────────→ sin dependencias
T-11 (theme_manager) ─→ necesita T-09, T-10
T-12 (data init) ─────→ necesita T-09 a T-11
─────────────────────────────
T-13 (pytest setup) ───→ sin dependencias
T-14 (tests widgets) ─→ necesita T-01, T-07, T-13
T-15 (tests data) ─────→ necesita T-09 a T-11, T-13
```

---

## Execution Order

**Fase A: UI Components**
1. T-01 → T-02 → T-03 → T-04 → T-05 → T-06 → T-07 → T-08
2. Manual verification: `python -m noctalia_color_scheme_manager.ui.mockup_preview`

**Fase B: Data Layer**
3. T-09 → T-10 → T-11 → T-12
4. Tests: T-14 → T-15

**Fase C: Integration**
5. Conectar ThemeManager → UI (signals)
6. Update mockup_preview para usar ThemeManager en vez de hardcoded data
