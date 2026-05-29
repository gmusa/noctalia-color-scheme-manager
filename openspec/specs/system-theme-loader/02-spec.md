# Spec: System Theme Loader

## Overview

Replace hardcoded theme data with dynamic loading from `~/.config/noctalia/colorschemes/`.

## Definitions

- **Theme file**: A `.json` or `.yaml` file in `~/.config/noctalia/colorschemes/` containing color definitions
- **Theme directory**: `~/.config/noctalia/colorschemes/`
- **Variant**: Either `dark` or `light` color scheme within a theme

## Theme File Format

### JSON Format (Primary)

```json
{
  "dark": {
    "mPrimary": "#RRGGBB",
    "mOnPrimary": "#RRGGBB",
    ...,
    "terminal": {
      "foreground": "#RRGGBB",
      "background": "#RRGGBB",
      "normal": { "black": "#RRGGBB", ... },
      "bright": { "black": "#RRGGBB", ... },
      "cursor": "#RRGGBB",
      "cursorText": "#RRGGBB",
      "selectionFg": "#RRGGBB",
      "selectionBg": "#RRGGBB"
    }
  },
  "light": { ... }
}
```

### YAML Format (Legacy)

Same structure as JSON, parsed via `yaml.safe_load()`.

## Functionality Specification

### 1. SystemThemeLoader Class

```python
class SystemThemeLoader:
    """Loads themes from the system themes directory."""
    
    THEMES_DIR = Path("~/.config/noctalia/colorschemes").expanduser()
    
    def list_themes(self) -> list[str]:
        """Return sorted list of theme names (directories)."""
        
    def load_theme(self, name: str) -> ThemeModel:
        """Load a theme by directory name."""
```

**Behavior**:
- Scan `THEMES_DIR` for subdirectories
- Each subdirectory contains exactly one theme file (`.json` preferred, `.yaml` fallback)
- Directory name becomes the theme display name
- Files must not be symlinks (security)

### 2. MainWindow Integration

**Sidebar Population**:
- On window creation, call `SystemThemeLoader().list_themes()`
- Populate sidebar list with discovered themes
- First theme is auto-selected by default
- Sidebar updates on window focus (optional enhancement)

**Theme Selection**:
- Clicking a sidebar button triggers `_on_theme_selected(name)`
- Load theme via `SystemThemeLoader().load_theme(name)`
- Pass loaded `ThemeModel` to `ThemeEditor`
- Update internal `_theme_name`, `_dark_colors`, `_light_colors`

**Empty State**:
- If no themes found, show "No themes found" in sidebar
- Subtle hint text: "Add themes to ~/.config/noctalia/colorschemes/"

**Error Handling**:
- Invalid theme file → skip with `logging.warning()`
- Missing file in directory → skip with warning
- Continue loading other themes even if one fails

### 3. File Format Support

| Format | Extension | Parser | Priority |
|--------|-----------|--------|----------|
| JSON | `.json` | `json.load()` | High |
| YAML | `.yaml` / `.yml` | `yaml.safe_load()` | Low (legacy) |

**Auto-detection**:
- Try `.json` first in each directory
- Fall back to `.yaml` if no JSON found
- Reject directory if neither exists

### 4. Data Flow

```
~/.config/noctalia/colorschemes/
    └── "monokai"/
        └── monokai.json
    └── "GitHub Dark"/
        └── GitHub Dark.json
    └── ...

SystemThemeLoader.list_themes()
    ↓
MainWindow._build_sidebar()
    ↓ [user clicks theme]
MainWindow._on_theme_selected(name)
    ↓
SystemThemeLoader.load_theme(name)
    ↓
ThemeModel (from theme_model.py)
    ↓
ThemeEditor(dark_colors, light_colors)
    ↓
MaterialEditor + TerminalEditor (apply colors)
```

## Acceptance Criteria

### AC1: Sidebar Population
- [ ] Sidebar shows all themes from `~/.config/noctalia/colorschemes/`
- [ ] Theme names are derived from directory names
- [ ] List is sorted alphabetically (case-insensitive)
- [ ] Empty sidebar shows "No themes found" message

### AC2: Theme Selection
- [ ] Clicking a theme button loads its colors
- [ ] Material editor displays the selected theme's colors
- [ ] Terminal editor displays the selected theme's colors
- [ ] Selection is visually indicated (active toggle state)

### AC3: Variant Support
- [ ] Both `dark` variant loads correctly
- [ ] Both `light` variant loads correctly
- [ ] Switching variants in editor reflects loaded data

### AC4: Error Handling
- [ ] Corrupt JSON/YAML files are skipped with warning
- [ ] Missing themes directory creates empty sidebar (no crash)
- [ ] Individual theme failures don't prevent loading others

### AC5: Code Quality
- [ ] No hardcoded color dictionaries in `MainWindow`
- [ ] All colors come from loaded `ThemeModel`
- [ ] `ThemeManager` continues to work for YAML themes
- [ ] Code passes linting (`ruff check`)

## File Changes

| File | Change |
|------|--------|
| `noctalia_color_scheme_manager/ui/main_window.py` | Replace hardcoded colors with SystemThemeLoader integration |
| `noctalia_color_scheme_manager/data/system_theme_loader.py` | **New**: SystemThemeLoader class |
| `noctalia_color_scheme_manager/data/__init__.py` | Export SystemThemeLoader |
| `noctalia_color_scheme_manager/data/theme_manager.py` | Add JSON format support |

## Dependencies

- `json` (stdlib)
- `pathlib` (stdlib)
- `logging` (stdlib)
- Existing: `theme_model.py`, `ThemeModel`
