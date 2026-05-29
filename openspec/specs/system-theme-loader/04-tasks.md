# Tasks: System Theme Loader Implementation

## Task List

### Phase 1: Core Infrastructure

- [ ] **T1**: Create `SystemThemeLoader` class in `data/system_theme_loader.py`
  - `list_themes()` - scan directories, return sorted names
  - `load_theme(name)` - load JSON/YAML, return ThemeModel
  - Security: reject symlinks, validate paths
  - Error handling: skip invalid dirs silently on list

- [ ] **T2**: Add JSON support to ThemeModel
  - `ThemeModel.from_json_dict(data)` - parse JSON format
  - Validate color values (reuse existing validation)

- [ ] **T3**: Export SystemThemeLoader in `data/__init__.py`

### Phase 2: UI Integration

- [ ] **T4**: Modify `MainWindow` to use SystemThemeLoader
  - Remove hardcoded DARK_COLORS, LIGHT_COLORS
  - Remove hardcoded theme list `["monokai", "GitHub Dark", "Oxocarbon"]`
  - Add `_on_theme_selected(name)` callback
  - Populate sidebar dynamically from loader

- [ ] **T5**: Connect theme selection to ThemeEditor
  - Pass loaded ThemeModel colors to ThemeEditor
  - Handle both dark and light variants

- [ ] **T6**: Add empty state UI
  - Show "No themes found" when directory is empty
  - Show hint about adding themes

### Phase 3: Polish

- [ ] **T7**: Add logging for skipped invalid themes
- [ ] **T8**: Update `ThemeEditor` to accept ThemeModel directly
- [ ] **T9**: Run `ruff check` and `ruff format`
- [ ] **T10**: Manual verification

## File Changes Summary

| Task | File | Lines (est.) |
|------|------|--------------|
| T1 | `data/system_theme_loader.py` | ~100 |
| T2 | `data/theme_model.py` | ~20 |
| T3 | `data/__init__.py` | ~5 |
| T4 | `ui/main_window.py` | ~60 |
| T5 | `ui/theme_editor.py` | ~20 |
| T6 | `ui/main_window.py` | ~10 |
| T7 | `data/system_theme_loader.py` | ~5 |
| T8 | `ui/theme_editor.py` | ~20 |
| T9 | various | - |
| T10 | - | - |

**Total estimated**: ~240 lines

## Dependencies

```
T1 → T2 (T1 creates loader, T2 adds JSON to ThemeModel)
T1, T2, T3 → T4 (all needed before UI integration)
T4 → T5 (UI integration depends on loader working)
T5 → T6 (empty state is part of T4)
T1-T6 → T7-T10 (polish phase)
```

## Review Workload

Estimated: ~240 lines across 5-6 files. Within single PR budget (~400 lines).

## Verification Steps

1. Run `python -m noctalia_color_scheme_manager.main`
2. Sidebar should show: "GitHub Dark", "monokai", "monokai-new", "Oxocarbon"
3. Click each theme → colors should change in Material and Terminal editors
4. Check terminal output for any warnings about invalid themes
5. Toggle dark/light variant → colors should switch
