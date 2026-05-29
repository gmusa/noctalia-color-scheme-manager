# Design: Noctalia Modular Refactor

## 1. Architecture Decision Records

### ADR-001: Mantener `mockup.py` como referencia

**Decisión**: No eliminar `ui/mockup.py` inmediatamente.

**Contexto**: El archivo monolith contiene la implementación original completa. Hay riesgo de "borrar y reescribir" sin rollback.

**Consecuencias**:
- ✅ Podemos verificar que `mockup_preview.py` replica el comportamiento
- ✅ Rollback simple si algo falla
- ⚠️ Técnico负债 temporal (dos versiones)

**Resolución**: Deprecar `mockup.py` con comment `# DEPRECATED: Use mockup_preview.py`, mover a `ui/deprecated/` cuando `mockup_preview.py` esté verificado.

---

### ADR-002: Dataclasses + Signals en lugar de GObject

**Decisión**: Usar `dataclasses` + callbacks manuales para el data model.

**Alternativas evaluadas**:

| Alternativa | Pros | Contras |
|-------------|------|---------|
| GObject subclass | Signals nativos GTK | Boilerplate, learning curve |
| `dataclasses` + callbacks | Simple, Pythonic | No binding automático |
| `attrs` + signals | Más features que dataclasses | Dependencia adicional |

**Decisión final**: `dataclasses` + callbacks manuales.

**Justificación**:
- GTK4 binding ya existe, no necesitamos más binding automático
- Mantiene el codebase simple
- Signals de GObject no dan beneficios concretos en este caso

**Tradeoff**: Necesitamos manualmente invocar callbacks cuando un color cambia. Aceptable para v1.

---

### ADR-003: YAML para storage de themes

**Decisión**: Usar YAML en lugar de JSON.

**Alternativas**:

| Alternativa | Pros | Cons |
|-------------|------|------|
| JSON | Estándar web, parsing rápido | Sin comentarios, verbose para humanos |
| YAML | Comments, legible, Noctalia usa YAML | Parser más pesado |

**Decisión final**: YAML.

**Justificación**: El usuario usa Noctalia que guarda en YAML. Mantener consistencia. PyYAML ya está en dependencies.

---

### ADR-004: Estructura de archivos del data layer

**Decisión**: Tres módulos separados: `theme_model.py`, `theme_manager.py`, `schema.py`.

**Alternativas**:

| Alternativa | Pros | Cons |
|-------------|------|------|
| Todo en `__init__.py` | Menos archivos | Violates SRP |
| Un `models.py` | Separación clara | Puede crecer mucho |
| Tres módulos | SRP, tests granulares | Más imports |

**Decisión final**: Tres módulos.

---

## 2. Module Design

### 2.1 Data Layer

```
data/
├── __init__.py          # from .theme_manager import ThemeManager
│                        # from .theme_model import ThemeModel
│                        # from .schema import Schema
├── theme_model.py       # Dataclasses + signal callbacks
├── theme_manager.py     # Filesystem operations
└── schema.py            # Validation functions
```

**theme_model.py**:
```python
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class TerminalColors:
    foreground: str = "#000000"
    background: str = "#ffffff"
    normal: dict[str, str] = field(default_factory=dict)
    bright: dict[str, str] = field(default_factory=dict)
    cursor: str = "#000000"
    cursorText: str = "#ffffff"
    selectionFg: str = "#000000"
    selectionBg: str = "#ffffff"

@dataclass
class VariantColors:
    mPrimary: str = "#000000"
    mOnPrimary: str = "#ffffff"
    # ... 15 more fields
    terminal: TerminalColors = field(default_factory=TerminalColors)

@dataclass
class ThemeModel:
    name: str
    dark: VariantColors = field(default_factory=VariantColors)
    light: VariantColors = field(default_factory=VariantColors)
    
    # Signal system
    _change_callbacks: list[Callable] = field(default_factory=list, repr=False)
    
    def on_change(self, callback: Callable) -> None:
        """Register a callback for theme changes."""
        self._change_callbacks.append(callback)
    
    def _notify_change(self) -> None:
        for cb in self._change_callbacks:
            cb(self)
    
    # Property setters that notify
    @property
    def mPrimary(self) -> str:
        return self.dark.mPrimary
    
    @mPrimary.setter
    def mPrimary(self, value: str) -> None:
        self.dark.mPrimary = value
        self._notify_change()
```

### 2.2 UI Layer

```
ui/
├── app.py              # App(Adw.Application)
├── main_window.py      # MainWindow(Adw.Bin)
├── variant_page.py    # VariantPage(Gtk.Box)
├── theme_editor.py    # ThemeEditor(Gtk.Box)
├── mockup_preview.py  # Demo con datos Monokai
└── deprecated/
    └── mockup.py       # Original monolith
```

---

## 3. Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                      ThemeManager                        │
│  list_themes() / load_theme() / save_theme()            │
└─────────────────────┬───────────────────────────────────┘
                      │ ThemeModel
                      ▼
┌─────────────────────────────────────────────────────────┐
│                     ThemeModel                           │
│  dark: VariantColors                                     │
│  light: VariantColors                                    │
│  on_change(callback) → _notify_change()                  │
└─────────────────────┬───────────────────────────────────┘
                      │ signal → UI update
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    UI Components                         │
│  VariantPage / MaterialEditor / TerminalEditor          │
│  Lee colors del ThemeModel, renderiza widgets           │
└─────────────────────────────────────────────────────────┘
```

**Nota**: La edición real (cambiar un color → actualizar ThemeModel) es v2. v1 solo muestra datos hardcodeados en mockup_preview.

---

## 4. Testing Strategy

### 4.1 GTK Widget Tests (pytest-lax)

pytest-lax permite tests funcionales de GTK sin X display:

```python
import pytest
from noctalia_color_scheme_manager.ui.widgets import ColorSwatch

@pytest.fixture
def app():
    from gi.repository import Gtk
    app = Gtk.Application()
    return app

def test_colorswatch_creates_with_color(app):
    swatch = ColorSwatch("#ff0000", app=app)
    assert swatch._color == "#ff0000"
```

### 4.2 Data Layer Tests (tmpfs)

```python
import pytest
import tempfile
from pathlib import Path
from noctalia_color_scheme_manager.data import ThemeManager

@pytest.fixture
def tmp_themes_dir(tmp_path):
    themes_dir = tmp_path / "colorschemes"
    themes_dir.mkdir()
    return themes_dir

def test_list_themes(tmp_themes_dir, monkeypatch):
    monkeypatch.setattr(ThemeManager, 'THEMES_DIR', tmp_themes_dir)
    (tmp_themes_dir / "monokai.yaml").write_text("...")
    manager = ThemeManager()
    assert "monokai" in manager.list_themes()
```

---

## 5. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| GTK imports fallan en CI | High | Low | Usar `pytest-lax` o skip en CI sin display |
| Duplicación de código entre mockup.py y mockup_preview | Medium | Medium | Comparar estructura visual al final |
| Dataclass signals no propagan correctamente | Medium | Low | Tests de roundtrip data → UI |
| YAML parsing lento para muchos themes | Low | Low | Lazy loading, cache en memoria |
