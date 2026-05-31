"""ENV loader for DataMap (.env files)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, ClassVar, Dict, List

from datamap.loaders.base import BaseLoader

_LINE_RE = re.compile(
    r"""
    ^\s*
    (?:export\s+)?          # optional 'export' keyword
    (?P<key>[A-Za-z_]\w*)   # variable name
    \s*=\s*
    (?P<value>
        "(?:[^"\\]|\\.)*"   # double-quoted value
        |
        '(?:[^'\\]|\\.)*'   # single-quoted value
        |
        [^\#\r\n]*          # unquoted value (strip trailing whitespace later)
    )
    \s*(?:\#.*)?$           # optional inline comment
    """,
    re.VERBOSE,
)


class EnvLoader(BaseLoader):
    """Загрузчик для файлов .env (формат key=value)."""

    extensions: ClassVar[List[str]] = [".env"]

    def load(self, path: Path) -> Any:
        self.validate(path)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except PermissionError as exc:
            raise PermissionError(f"Permission denied: {path}") from exc

        result: Dict[str, str] = {}
        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            # skip blanks and comments
            if not stripped or stripped.startswith("#"):
                continue
            m = _LINE_RE.match(line)
            if not m:
                raise ValueError(
                    f"Invalid .env syntax in '{path}' at line {lineno}: {line!r}"
                )
            key = m.group("key")
            raw = m.group("value").strip()
            # strip surrounding quotes and unescape
            if (raw.startswith('"') and raw.endswith('"')) or (
                raw.startswith("'") and raw.endswith("'")
            ):
                raw = raw[1:-1].replace("\\'", "'").replace('\\"', '"')
            result[key] = raw

        return result

    def description(self) -> str:
        return "ENV loader  (.env) — dotenv-style key=value parser"
