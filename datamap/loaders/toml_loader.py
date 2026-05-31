"""TOML loader for DataMap."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, ClassVar, List

from datamap.loaders.base import BaseLoader


class TOMLLoader(BaseLoader):
    """Loads ``.toml`` files.

    Uses the stdlib ``tomllib`` on Python 3.11+, falls back to
    the ``tomli`` third-party package on older versions.
    """

    extensions: ClassVar[List[str]] = [".toml"]

    def _get_tomllib(self):  # type: ignore[return]
        if sys.version_info >= (3, 11):
            import tomllib
            return tomllib
        try:
            import tomli as tomllib  # type: ignore[no-redef]
            return tomllib
        except ImportError as exc:
            raise ImportError(
                "tomli is required for TOML support on Python < 3.11.  "
                "Install it with:  pip install tomli"
            ) from exc

    def load(self, path: Path) -> Any:
        self.validate(path)
        tomllib = self._get_tomllib()
        try:
            with path.open("rb") as fh:
                return tomllib.load(fh)
        except PermissionError as exc:
            raise PermissionError(f"Permission denied: {path}") from exc
        except Exception as exc:
            raise ValueError(f"Invalid TOML in '{path}' — {exc}") from exc

    def description(self) -> str:
        return "TOML loader  (.toml) — tomllib / tomli"
