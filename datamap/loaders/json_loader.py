"""JSON loader for DataMap."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar, List

from datamap.loaders.base import BaseLoader


class JSONLoader(BaseLoader):
    """Загрузчик для файлов в формате JSON (использует стандартную библиотеку json)."""

    extensions: ClassVar[List[str]] = [".json"]

    def load(self, path: Path) -> Any:
        self.validate(path)
        try:
            text = path.read_text(encoding="utf-8")
        except PermissionError as exc:
            raise PermissionError(f"Permission denied: {path}") from exc

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in '{path}' — {exc.msg} "
                f"(line {exc.lineno}, col {exc.colno})"
            ) from exc

    def description(self) -> str:
        return "JSON loader  (.json) — stdlib json"
