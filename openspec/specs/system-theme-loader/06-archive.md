# Archive: System Theme Loader

## Status: COMPLETED

## Summary

Replaced hardcoded theme colors with dynamic loading from `~/.config/noctalia/colorschemes/`.

### Files Changed

| File | Change |
|------|--------|
| `data/system_theme_loader.py` | NEW - SystemThemeLoader class |
| `data/__init__.py` | Export SystemThemeLoader |
| `ui/main_window.py` | Refactored - no more hardcoded colors |
| `ui/app.py` | Minor lint fix |
| `ui/widgets/color_tile.py` | Added initial_color parameter |
| `ui/editors/terminal_editor.py` | Fixed for terminal nested keys |

### Verification

- All 4 themes load: GitHub Dark, monokai, monokai-new, Oxocarbon
- Both dark/light variants work
- Terminal editor shows correct colors
- Lint passes

## Timestamp

Completed: 2026-05-29
