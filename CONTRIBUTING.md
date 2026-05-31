# Contributing to DataMap 🎉

Thank you for taking the time to contribute! DataMap is a community-driven project and every contribution — big or small — makes it better.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Setting Up the Development Environment](#setting-up-the-development-environment)
- [Running Tests](#running-tests)
- [Adding a New Loader (Plugin)](#adding-a-new-loader-plugin)
- [Commit Style](#commit-style)
- [Pull Request Checklist](#pull-request-checklist)

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.
Be respectful and constructive in all discussions.

---

## How Can I Contribute?

| Type | Where |
|------|-------|
| 🐛 Bug report | [Issues](https://github.com/stefrim-Z/DataMap/issues/new?template=bug_report.md) |
| 💡 Feature request | [Issues](https://github.com/stefrim-Z/DataMap/issues/new?template=feature_request.md) |
| 📖 Documentation | Edit any `.md` file or the docstrings in source |
| 🔌 New loader | See [Adding a New Loader](#adding-a-new-loader-plugin) |
| ⭐ Star the repo | Always appreciated! |

---

## Setting Up the Development Environment

```bash
# 1. Fork + clone
git clone https://github.com/YOUR_FORK/datamap.git
cd datamap

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install in editable mode with all dev extras
pip install -e ".[dev]"

# 4. Verify setup
datamap examples/sample.json
```

---

## Running Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=datamap --cov-report=term-missing

# Single file
pytest tests/test_core.py -v
```

We require **≥ 90 % coverage** on new code.

---

## Adding a New Loader (Plugin)

DataMap discovers loaders automatically — no registration needed!

1. Create `datamap/loaders/my_format_loader.py`
2. Subclass `BaseLoader` and declare `extensions`

```python
# datamap/loaders/my_format_loader.py
from pathlib import Path
from typing import Any, ClassVar, List
from datamap.loaders.base import BaseLoader

class MyFormatLoader(BaseLoader):
    extensions: ClassVar[List[str]] = [".myext"]

    def load(self, path: Path) -> Any:
        self.validate(path)
        # parse the file …
        return parsed_data
```

3. Add a test in `tests/test_loaders.py`
4. Submit a PR 🚀

---

## Commit Style

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add SQL dump loader
fix: handle BOM in UTF-8 .env files
docs: add loader plugin guide
test: cover EnvLoader edge cases
chore: bump rich to 13.7
```

---

## Pull Request Checklist

- [ ] Tests pass (`pytest`)
- [ ] Linting passes (`ruff check datamap tests`)
- [ ] Types pass (`mypy datamap`)
- [ ] Docstrings updated for new public API
- [ ] `CHANGELOG.md` entry added under `[Unreleased]`
- [ ] PR description explains *what* and *why*

Thank you — we ❤️ your contribution!
