# Color Theme Editor — Noctalia

## Overview

GUI application to create and edit color themes for the Noctalia Wayland compositor.

**Stack**: Python + GTK4 + libadwaita

---

## Scope

### In Scope
- Edit existing themes (JSON as source of truth)
- Create new themes from existing JSON as template
- Live preview of theme changes
- Persist to `~/.config/noctalia/colorschemes/`

### Out of Scope
- Export to other formats (CSS, KDE, etc.)
- Theme discovery/install from remote sources
- Any config beyond colors

---

## Theme Schema

Themes live at: `~/.config/noctalia/colorschemes/<name>/<name>.json`

```json
{
  "dark": { ... },
  "light": { ... }
}
```

Each variant contains:

### Material Design Tokens
| Key | Purpose |
|-----|---------|
| `mPrimary` | Primary accent color |
| `mOnPrimary` | Text/icon color on primary |
| `mSecondary` | Secondary accent |
| `mOnSecondary` | Text/icon on secondary |
| `mTertiary` | Tertiary accent |
| `mOnTertiary` | Text/icon on tertiary |
| `mError` | Error/destructive color |
| `mOnError` | Text on error |
| `mSurface` | Main background surface |
| `mOnSurface` | Text on surface |
| `mSurfaceVariant` | Elevated surface |
| `mOnSurfaceVariant` | Text on elevated surface |
| `mOutline` | Borders/dividers |
| `mShadow` | Shadow color |
| `mHover` | Hover state background |
| `mOnHover` | Text on hover |

### Terminal Colors
`terminal` key contains:

- `foreground` / `background`
- `cursor`, `cursorText`
- `selectionFg`, `selectionBg`
- `normal` / `bright`: 8-color ANSI palette (black, red, green, yellow, blue, magenta, cyan, white)

---

## UI Structure

```
AdwPreferencesWindow
├── OverviewPage (live preview)
├── MaterialColorsPage (dark mode tab + light mode tab)
└── TerminalColorsPage (dark mode tab + light mode tab)
```

### Per-color widget
- Color swatch (visual)
- Hex input (validated)
- GTK color picker button

---

## Technical Approach

### Data Layer
- `ThemeManager`: Load/save/list themes from filesystem
- `ThemeModel`: In-memory representation of current theme
- `JsonSchema`: Validation against the schema above

### UI Layer
- `MainWindow` (AdwPreferencesWindow)
- `OverviewPage`: Preview of both variants
- `ColorEditorPage`: Reusable widget for editing a single color
- `VariantTabs`: Dark/Light tab switcher

### Key Features
- Live preview updates on color change
- Undo/redo (per session)
- Backup before save (optional)
- Atomic file writes (temp file → rename)

---

## File Structure (TBD)

```
src/
├── __main__.py
├── app.py              # Window setup
├── data/
│   ├── theme_manager.py # FS operations
│   ├── theme_model.py  # Data model
│   └── schema.py       # Validation
├── ui/
│   ├── overview.py
│   ├── material_editor.py
│   └── terminal_editor.py
└── widgets/
    └── color_tile.py   # Single color widget
```

---

## Next Steps

1. Confirm project structure
2. Define initial mockups/wireframes
3. Implement data layer (theme_manager + theme_model)
4. Build UI scaffolding
5. Implement color editor widget
6. Connect data ↔ UI with live preview