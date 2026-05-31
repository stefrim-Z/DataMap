"""
BaseLoader — abstract contract that every DataMap loader must satisfy.

Third-party loaders just need to:
  1. Subclass ``BaseLoader``
  2. Declare the file ``extensions`` they handle
  3. Implement ``load(path) -> Any``

DataMap will discover them automatically if the module is placed inside
the ``datamap/loaders/`` directory (or installed as a plugin package that
registers the ``datamap.loaders`` entry-point group).
"""

from __future__ import annotations

import abc
from pathlib import Path
from typing import Any, ClassVar, List


class BaseLoader(abc.ABC):
    """
    Абстрактный базовый класс для всех загрузчиков файлов в DataMap.
    
    Каждый загрузчик должен:
    1. Наследовать этот класс.
    2. Указать поддерживаемые расширения в атрибуте `extensions`.
    3. Реализовать метод `load(path)`.
    """

    # Subclasses declare which file extensions they handle, e.g. [".json"]
    extensions: ClassVar[List[str]] = []

    @abc.abstractmethod
    def load(self, path: Path) -> Any:
        """
        Parse *path* and return the data as a Python object (dict / list / …).

        Raises
        ------
        FileNotFoundError
            If *path* does not exist.
        PermissionError
            If the process cannot read *path*.
        ValueError
            If the file content cannot be parsed.
        """

    # ------------------------------------------------------------------
    # Optional hooks — override for custom behaviour
    # ------------------------------------------------------------------

    def validate(self, path: Path) -> None:
        """
        Pre-load validation hook.  Raise an exception early if the loader
        cannot handle *path* (wrong magic bytes, etc.).
        Default implementation just checks existence and readability.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a regular file: {path}")

    def description(self) -> str:
        """Human-readable loader description shown in ``datamap --info``."""
        return f"{self.__class__.__name__} ({', '.join(self.extensions)})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} extensions={self.extensions}>"
