<div align="center">

```
 ██████╗  █████╗ ████████╗ █████╗ ███╗   ███╗ █████╗ ██████╗
 ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗████╗ ████║██╔══██╗██╔══██╗
 ██║  ██║███████║   ██║   ███████║██╔████╔██║███████║██████╔╝
 ██║  ██║██╔══██║   ██║   ██╔══██║██║╚██╔╝██║██╔══██║██╔═══╝
 ██████╔╝██║  ██║   ██║   ██║  ██║██║ ╚═╝ ██║██║  ██║██║
 ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
```

**Stop squinting at raw JSON. Start _seeing_ your data.**

[![PyPI version](https://img.shields.io/pypi/v/datamap?color=00d2ff&label=PyPI&style=for-the-badge)](https://pypi.org/project/datamap/)
[![Python](https://img.shields.io/pypi/pyversions/datamap?color=ffd700&style=for-the-badge)](https://pypi.org/project/datamap/)
[![CI](https://img.shields.io/github/actions/workflow/status/stefrim-Z/DataMap/ci.yml?branch=main&label=CI&style=for-the-badge)](https://github.com/stefrim-Z/DataMap/actions)
[![Coverage](https://img.shields.io/codecov/c/github/stefrim-Z/DataMap?color=00c853&style=for-the-badge)](https://codecov.io/gh/stefrim-Z/DataMap)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/stefrim-Z/DataMap?color=ff6b6b&style=for-the-badge)](https://github.com/stefrim-Z/DataMap/stargazers)

</div>

---

## ✨ What is DataMap?

DataMap is a **zero-config CLI tool** that transforms any `JSON`, `YAML`, `TOML`, or `.env` file into a gorgeous, **color-coded tree** right in your terminal — with a full **interactive TUI**, real-time **fuzzy search**, and one-command **SVG/HTML export** for beautiful documentation.

```
$ datamap examples/sample.json
```

```
╭─────────────────────────── sample.json · 512 B ──────────────────────────────╮
│ sample.json                                                                    │
│ ├── name: "DataMap"  [str·7]                                                  │
│ ├── version: 1  [int]                                                         │
│ ├── active: True  [bool]                                                      │
│ ├── tags: […]  [3 items]                                                      │
│ │   ├── 0: "cli"  [str]                                                       │
│ │   ├── 1: "python"  [str]                                                    │
│ │   └── 2: "rich"  [str]                                                      │
│ ├── author: {…}  [3 keys]                                                     │
│ │   ├── name: "DataMap Contributors"  [str]                                   │
│ │   ├── github: "https://github.com/…"  [str]                                │
│ │   └── languages: […]  [2 items]                                             │
│ └── nothing: null  [null]                                                     │
╰────────────────────────────────────────────────────────────────────────────────╯
```

---

## 🤔 Why DataMap?

Every developer knows the pain:

| Problem | What you do today | What DataMap gives you |
|---------|-------------------|------------------------|
| 🔥 **JSON Hell** | `cat config.json \| python -m json.tool` → wall of text | Beautiful color-coded tree, instantly |
| 😵 **Config Blindness** | Open file in editor, scroll endlessly | Interactive TUI: navigate, search, inspect in seconds |
| 📄 **Documentation Drag** | Screenshot terminal, paste into Notion | `datamap export` → pixel-perfect SVG in one command |
| 🔌 **Format Lock-in** | Separate tools for JSON / YAML / TOML / .env | One tool, all formats, pluggable for more |
| 🐢 **Big File Panic** | jq crashes, editor hangs | Background-threaded TUI stays smooth at 5 MB+ |

> **DataMap is the `cat` command you always wished existed.**

## 🚀 Installation

### Via Pip (Recommended)

To use DataMap as a standalone CLI tool:
```bash
pip install datamap
```

### From Source (Development Mode)

If you have cloned this repository and want to contribute or modify the code:
```bash
# Navigate to the project directory
cd DataMap

# Install in editable mode with all dependencies
pip install -e ".[all]"
```

---

## 📖 Usage

### 🌲 Visualize a File (CLI)

The simplest way to view your data as a tree:
```bash
# Provide the command and the path to your file
datamap config.json
datamap settings.yaml
datamap pyproject.toml
datamap .env
```

### 🔍 Limit Depth

For very large files, you can limit the recursion depth:
```bash
datamap config.json --depth 2
```

### 🖥️ Interactive Mode (TUI)

For deep data exploration with real-time search:
```bash
datamap tui config.json
```
*   **Arrow Keys**: Navigate the tree.
*   **F**: Focus the fuzzy search bar.
*   **Q**: Quit.

### 📤 Export to SVG or HTML

Perfect for embedding in documentation or reports:
```bash
datamap export config.json --format svg
datamap export settings.yaml --format html --output ./docs/tree.html
```

---

## 🧪 Practical Testing

To test DataMap with sample data without full installation:

1. Create a test directory and some sample files.
2. Point Python to the source code:
   ```powershell
   $env:PYTHONPATH = "C:\Path\To\DataMap"
   ```
3. Run the analyzer directly:
   ```powershell
   python -m datamap.core path/to/your/test/file.json
   ```

---

## 🔌 Using as a Library

You can integrate DataMap's logic directly into your own Python projects:

```python
from datamap.core import DataAnalyzer
from pathlib import Path

# Initialize the analyzer
analyzer = DataAnalyzer(Path("data.json"))

# Load and analyze data
data = analyzer.load()
tree = analyzer.build_tree(analyzer.analyse(data))

# Render to console using Rich
from rich.console import Console
Console().print(tree)
```

### ℹ️ Show registered loaders

```bash
datamap info
```

```
Registered DataMap loaders:
  .env   →  EnvLoader
  .json  →  JSONLoader
  .toml  →  TOMLLoader
  .yaml  →  YAMLLoader
  .yml   →  YAMLLoader
```

---

## 🔌 Plugin System

DataMap supports **zero-boilerplate plugins**. Drop a file in `datamap/loaders/` and it's automatically discovered:

```python
# datamap/loaders/csv_loader.py
import csv
from pathlib import Path
from typing import Any, ClassVar, List
from datamap.loaders.base import BaseLoader

class CSVLoader(BaseLoader):
    extensions: ClassVar[List[str]] = [".csv"]

    def load(self, path: Path) -> Any:
        self.validate(path)
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
```

That's it. Run `datamap info` to confirm it's registered. No setup, no config, no imports.

---

## 📦 Supported Formats

| Format | Extension(s) | Loader | Extra dep? |
|--------|-------------|--------|------------|
| JSON | `.json` | `JSONLoader` | — |
| YAML | `.yaml`, `.yml` | `YAMLLoader` | `pyyaml` (auto-installed) |
| TOML | `.toml` | `TOMLLoader` | stdlib on 3.11+; `tomli` on 3.9–3.10 |
| Dotenv | `.env` | `EnvLoader` | — |
| *(Your format)* | *(anything)* | *(your loader)* | *(optional)* |

---

## 🏗️ Project Structure

```
datamap/
├── datamap/
│   ├── __init__.py      # package entry
│   ├── core.py          # DataAnalyzer + Rich tree + CLI
│   ├── app.py           # Textual TUI
│   ├── export.py        # SVG / HTML export
│   └── loaders/
│       ├── __init__.py  # auto-discovery registry
│       ├── base.py      # BaseLoader contract
│       ├── json_loader.py
│       ├── yaml_loader.py
│       ├── toml_loader.py
│       └── env_loader.py
├── tests/
│   ├── test_core.py
│   └── test_loaders.py
├── examples/
│   ├── sample.json
│   ├── sample.yaml
│   └── sample.env
├── .github/workflows/
│   ├── ci.yml           # Test matrix (3.9–3.12 × 3 OSes)
│   └── codeql.yml       # Security scanning
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=datamap --cov-report=term-missing

# Lint
ruff check datamap tests

# Type check
mypy datamap
```

CI runs automatically on every push across **Python 3.9, 3.10, 3.11, 3.12** on **Ubuntu, Windows, and macOS**.

---

## 🤝 Contributing

Contributions are what make the open-source community amazing. Whether you're fixing a bug, adding a loader for a new format, or improving the docs — **you're welcome here**.

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide.

**Quick start:**

```bash
git clone https://github.com/YOUR_FORK/datamap.git
cd datamap
pip install -e ".[dev]"
pytest   # make sure everything passes
# → make your changes
# → open a PR 🎉
```

---

## 💡 Roadmap

- [ ] **SQL dump loader** — visualize table schemas and row previews
- [ ] **Protobuf / MessagePack** loader
- [ ] **Side-by-side diff mode** — compare two files visually
- [ ] **Watch mode** — auto-reload tree when file changes
- [ ] **VS Code extension** — inline tree preview in editor
- [ ] **GitHub Action** — comment data diffs on PRs

Have an idea? [Open an issue!](https://github.com/stefrim-Z/DataMap/issues/new)

---

## ⭐ Show Your Support

If DataMap saved you time, please consider:

- ⭐ **Starring this repository** — it helps others discover DataMap
- 🐦 **Sharing on Twitter/X** — tag `#datamap` and `#python`
- 📦 **Recommending to your team** — add to your project's `CONTRIBUTING.md`

---

## 📄 License

DataMap is released under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ and `rich` colors by the DataMap community.

**[⭐ Star DataMap](https://github.com/stefrim-Z/DataMap)** · **[🐛 Report Bug](https://github.com/stefrim-Z/DataMap/issues)** · **[💡 Request Feature](https://github.com/stefrim-Z/DataMap/issues)**

</div>
