# AGENTS.md

## Project Overview

**noctalia-color-scheme-manager** — A GTK GUI application for creating and editing color themes for Noctalia. Built with PyGObject and PyYAML.

## Dev Environment

- **Python**: >=3.12
- **Virtual environment**: `.venv/` (activate with `source .venv/bin/activate`)
- **Install deps**: `pip install -e ".[dev]"`
- **Install pre-commit**: `pip install pre-commit` (if not present)

## Build & Test Commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run the application
python -m noctalia_color_scheme_manager.main
# or
nctheme

# Run tests
./test.sh

# Lint
ruff check .

# Format
ruff format .
```

## Code Style

- **Line length**: 100 characters (see `pyproject.toml`)
- **Quotes**: Single quotes preferred
- **Type checking**: pyright (config in `pyrightconfig.json`)
- **Linting**: ruff with default rules

## Architecture Notes

```
noctalia_color_scheme_manager/
├── main.py              # Entry point
├── theme_loader.py      # Load/parse theme files
├── theme_writer.py     # Write themes
├── ui/
│   ├── main_window.py   # Main GTK window
│   └── dialogs/         # Dialog components
├── utils/
│   └── color_utils.py   # Color conversion utilities
└── models/
    └── theme.py         # Theme data models
```

## Language Policy

**All documentation, code, specs, and artifacts must be in English.**

This includes:
- Docstrings and comments
- README, AGENTS.md, and any documentation
- Specs (OpenSpec artifacts)
- Issue descriptions and PR titles
- Variable and function names

Exception: User-facing UI strings may use the project's target language when appropriate.


## OpenSpec / SDD Workflow

For significant changes, use the OpenSpec SDD workflow:
1. Create `openspec/` directory with `config.yaml`
2. Follow proposal → spec → design → tasks → apply → verify phases
3. See `.pi/` directory for Pi agent configurations

## Important Conventions

- Theme files are YAML format
- Color values should support both hex (`#RRGGBB`) and CSS rgb/rgba formats
- The application must handle invalid theme files gracefully with user-friendly error messages