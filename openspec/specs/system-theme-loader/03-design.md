# Design: System Theme Loader

## Architecture Decision

### Option A: Extend ThemeManager (Chosen)

Add JSON support to the existing `ThemeManager` class and use it for both listing and loading.

**Pros**:
- Reuses existing code
- Consistent API for theme operations
- Centralized theme handling

**Cons**:
- ThemeManager was designed for YAML files in flat directory
- Needs refactoring to handle subdirectories and JSON

### Option B: New SystemThemeLoader Class

Create a separate loader specifically for the UI's sidebar.

**Pros**:
- Clear separation of concerns
- UI doesn't need to know about ThemeManager's internal details
- Easier to test in isolation

**Cons**:
- Duplication of theme loading logic
- Two classes to maintain

### Decision: Option B (New SystemThemeLoader)

Rationale: The UI's sidebar has different requirements than ThemeManager (directory scanning vs file-based). ThemeManager remains for YAML theme management (create/save/delete). SystemThemeLoader is purpose-built for loading themes into the UI.

## Class Design

### SystemThemeLoader

```python
from pathlib import Path
import json
import logging
from typing import Optional

from .theme_model import ThemeModel


class SystemThemeLoader:
    """Loads themes from ~/.config/noctalia/colorschemes/ for UI display."""
    
    THEMES_DIR = Path("~/.config/noctalia/colorschemes").expanduser()
    
    def __init__(self, themes_dir: Optional[Path] = None) -> None:
        self._themes_dir = themes_dir or self.THEMES_DIR
    
    def list_themes(self) -> list[str]:
        """Scan themes directory and return sorted theme names."""
    
    def load_theme(self, name: str) -> ThemeModel:
        """Load theme by directory name.
        
        Raises:
            FileNotFoundError: Theme directory doesn't exist
            ValueError: No valid theme file in directory
        """
```

### Key Design Points

1. **Directory-based**: Themes are in subdirectories (e.g., `monokai/monokai.json`)
2. **Format priority**: JSON > YAML (JSON is the standard for Noctalia)
3. **Silent failures**: Invalid themes are skipped, not errors
4. **No symlinks**: Security measure to prevent path traversal

## Sequence Diagram: Theme Selection

```
User clicks "monokai" button
        ↓
MainWindow._on_theme_selected("monokai")
        ↓
SystemThemeLoader.load_theme("monokai")
        ↓
Scan ~/.config/noctalia/colorschemes/monokai/
        ↓
Find monokai.json → parse with json.load()
        ↓
Create ThemeModel.from_dict(data)
        ↓
Pass to ThemeEditor(dark=theme.dark, light=theme.light)
        ↓
MaterialEditor and TerminalEditor receive new colors
```

## Tradeoffs

| Tradeoff | Decision | Rationale |
|----------|----------|-----------|
| JSON vs YAML priority | JSON first | JSON is the primary format per spec observation |
| Fail-silent vs fail-hard | Silent for listing, raise for loading | Don't crash UI on bad files |
| Caching themes | No caching | Themes change rarely; reload each time |
| Real-time directory monitoring | No | Future enhancement, out of scope |

## Security Considerations

1. **Path traversal**: Reject `..` in theme names
2. **Symlinks**: Reject theme files that are symlinks
3. **Path validation**: Resolve paths and verify they're within themes_dir
4. **File size limits**: Not implemented (future enhancement)

## Testing Strategy

```python
# tests/test_system_theme_loader.py
def test_list_themes_returns_sorted_names():
    # Mock filesystem, verify alphabetical sort

def test_load_theme_parses_json():
    # Mock JSON file, verify ThemeModel created

def test_skips_invalid_directories():
    # Empty dir, no .json/.yaml, symlink → skip

def test_load_theme_raises_for_missing():
    # Nonexistent theme → FileNotFoundError
```

## Open Questions

1. **Should we cache loaded themes?**
   - Current decision: No. Simpler, always fresh.
   - Revisit if performance becomes an issue.

2. **Should themes be reloadable?**
   - Current decision: Yes, by re-calling load_theme().
   - ThemeEditor will be updated to accept new ThemeModel.
