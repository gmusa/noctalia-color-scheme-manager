# Proposal: Refactor Modular Architecture

## Problem Statement

El archivo `ui/mockup.py` (600+ líneas) es un monolith que mezcla:
- **Widgets primitivos**: ColorSwatch, ColorTile, ContrastTile
- **Editores complejos**: MaterialEditor, TerminalEditor
- **Composición de UI**: VariantPage, ThemeEditor, MainWindow, App
- **Lógica de preview**: PreviewPanel inline
- **Datos de prueba**: Monokai colors hardcodeados en MainWindow

**Síntomas:**
1. No hay separación entre UI reutilizable y lógica de aplicación
2. Imposible testear widgets aisladamente
3. Duplicación: `_build_material_preview` existe 3 veces
4. `main.py` es un stub que no inicia la aplicación real
5. Sin data layer → no hay persistencia ni validación

## Goal

Extraer módulos reutilizables con tests funcionales, preparando la base para:
- Persistencia de themes (JSON en `~/.config/noctalia/colorschemes`)
- Validación contra schema Noctalia
- Señales para sincronizar data ↔ UI

## Non-Goals

- No reescribir los widgets/editors que ya funcionan en `mockup.py`
- No implementar features de edición real (solo scaffolding con signals)
- No cambiar la apariencia visual actual

## Success Metrics

| Métrica | Target |
|---------|--------|
| Archivos en `ui/` | ≤ 10 (vs ~15 planned) |
| Líneas en `mockup.py` residual | < 100 |
| Test coverage para widgets | 100% |
| Test coverage para editors | 80% |
| Data layer puede list/save themes | ✅ |

## Scope

**Incluye:**
- Extraer MainWindow, VariantPage, ThemeEditor a módulos propios
- Crear `mockup_preview.py` como demo funcional
- Implementar Phase 4 (data layer) completo
- Tests con pytest-lax (GTK functional)

**Excluye:**
- Rewriting de widgets/editors ya modularizados
- Cambio de look & feel
- Señales de edición bidireccional (v2)

## Open Questions

1. ¿Mantener `mockup.py` como referencia o deprecarlo?
2. ¿El data layer usa yaml o json para themes?
3. ¿pytest-lax o pytest con pytest-xvfb para GTK?
