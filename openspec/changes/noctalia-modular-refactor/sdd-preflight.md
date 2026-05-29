# SDD Session Preflight — noctalia-modular-refactor

**Date**: 2026-05-28
**Scope**: Full SDD (all phases)
**Artifact Store**: both (openspec + engram)
**Execution Mode**: interactive

## Decisions

| Decision | Value | Rationale |
|----------|-------|-----------|
| Alcance | SDD completo | Refactor completo: widgets → editors → UI → data |
| Testing | pytest-lax | GTK functional tests sin mocks |
| Artifacts | ambos | openspec/ versionado + engram persistente |
| Modo | interactive | Pausa entre fases para revisión |

## SDD Triggers Satisfied

- [x] Unclear requirements → plan existente pero necesita formalización
- [x] Architectural decisions → modular architecture con data layer
- [x] Cross-cutting behavior → signals/properties para data→UI
- [x] Expected large diff → 15+ archivos

## Constraints

- Mantener `ui/mockup.py` como referencia hasta completar integración
- Compatibilidad con GTK4 + libadwaita
- No romper la demo actual hasta que mockup_preview esté funcional
