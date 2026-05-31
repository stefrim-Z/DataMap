# Changelog

All notable changes to DataMap will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [1.0.0] — 2026-05-31

### Added
- `DataAnalyzer` core with type-aware Rich tree rendering
- Color palette: bold cyan keys, green strings, gold numbers, purple booleans, dim red nulls
- Pluggable loader system with auto-discovery (`BaseLoader`)
- Built-in loaders: JSON, YAML, TOML, `.env`
- SVG & HTML export via `Rich` record mode (`datamap export`)
- Interactive Textual TUI with real-time fuzzy search (`datamap tui`)
- Keyboard shortcuts: `C` collapse, `E` expand, `F` focus search, `Q` quit
- `pyproject.toml` packaging with Hatch; `pip install .` → `datamap` command
- Full CI matrix: Python 3.9–3.12 × Ubuntu / Windows / macOS
- CodeQL security scanning
- ASCII logo on startup
- `--depth` and `--no-meta` flags
- `datamap info` command to list registered loaders

[Unreleased]: https://github.com/stefrim-Z/DataMap/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/stefrim-Z/DataMap/releases/tag/v1.0.0
