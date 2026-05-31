"""YAML loader for DataMap."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from datamap.loaders.base import BaseLoader


class YAMLLoader(BaseLoader):
    """Загрузчик для файлов в формате YAML (использует PyYAML)."""

    extensions: ClassVar[list[str]] = [".yaml", ".yml"]

    def load(self, path: Path) -> Any:
        self.validate(path)
        try:
            import yaml  # optional dependency
        except ImportError as exc:
            raise ImportError(
                "PyYAML is required for YAML support.  Install it with:  pip install pyyaml"
            ) from exc

        try:
            text = path.read_text(encoding="utf-8")
        except PermissionError as exc:
            raise PermissionError(f"Permission denied: {path}") from exc

        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in '{path}' — {exc}") from exc

    def description(self) -> str:
        return "YAML loader  (.yaml, .yml) — PyYAML safe_load"
