# Proposal: Load Themes from System Configuration Directory

## Problem Statement

The application currently uses hardcoded color definitions in `main_window.py` (DARK_COLORS and LIGHT_COLORS). This creates maintenance issues:

1. **Stale data**: Colors don't reflect actual theme files users may have
2. **Manual sync**: Theme list must be manually updated when new themes are added
3. **Inconsistency**: The existing `ThemeManager` class exists but is unused by the UI
4. **UX gap**: Users cannot load their own themes from `~/.config/noctalia/colorschemes/`

## Proposed Solution

Replace hardcoded data with dynamic loading from the system themes directory (`~/.config/noctalia/colorschemes/`).

### Scope

- Load available themes by scanning the themes directory
- Populate sidebar with discovered themes
- On theme selection, load colors from the theme file and apply to both Material and Terminal editors
- Support both `dark` and `light` variants
- Handle both JSON and YAML theme formats

### Out of Scope

- Theme creation/deletion/modification (already exists in ThemeManager)
- Theme validation beyond basic structure checks
- Multiple theme directories (single source: `~/.config/noctalia/colorschemes/`)

## Acceptance Criteria

1. Sidebar displays all themes found in `~/.config/noctalia/colorschemes/`
2. Selecting a theme in the sidebar loads its colors into the Material editor
3. Selecting a theme in the sidebar loads its colors into the Terminal editor
4. Both `dark` and `light` variants are loaded and can be switched
5. Empty/missing themes directory shows empty sidebar with helpful message
6. Invalid theme files are skipped with a logged warning
7. Theme selection is reflected in UI immediately

## Technical Approach

1. Create a `SystemThemeLoader` class to scan directories and load theme files
2. Extend `ThemeManager` to support JSON format (in addition to YAML)
3. Integrate loader with `MainWindow` sidebar population
4. Connect theme selection to existing `ThemeEditor` via callbacks

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| JSON/YAML format mismatch | Medium | Medium | Implement format auto-detection |
| Missing themes directory | Low | Low | Create directory if missing, show empty state |
| Corrupt theme files | Medium | Low | Skip with warning, don't crash |
| Backwards compatibility with YAML-only ThemeManager | Low | Low | Add JSON support without removing YAML |
