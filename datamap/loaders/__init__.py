"""
DataMap Loaders — pluggable file format support.

Loaders are auto-discovered from this package.  Any module that defines a
subclass of ``BaseLoader`` will be picked up automatically when DataMap
resolves a file extension.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from datamap.loaders.base import BaseLoader


def _discover_loaders() -> dict[str, type[BaseLoader]]:
    """
    Walk every module in the loaders package and collect all BaseLoader
    subclasses, keying them by the extensions they declare.
    """
    registry: dict[str, type[BaseLoader]] = {}
    package_dir = Path(__file__).parent

    for _finder, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        if module_name == "base":
            continue
        full_name = f"datamap.loaders.{module_name}"
        try:
            module = importlib.import_module(full_name)
        except ImportError:
            continue

        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            try:
                if isinstance(obj, type) and issubclass(obj, BaseLoader) and obj is not BaseLoader:
                    for ext in obj.extensions:
                        registry[ext.lower()] = obj
            except TypeError:
                pass

    return registry


LOADER_REGISTRY: dict[str, type[BaseLoader]] = _discover_loaders()


def get_loader(path: Path) -> BaseLoader:
    """Return an appropriate loader instance for *path*, or raise ValueError."""
    ext = path.suffix.lower()

    # Handle files like .env (where suffix might be empty)
    if not ext and path.name.startswith("."):
        ext = path.name.lower()

    cls = LOADER_REGISTRY.get(ext)
    if cls is None:
        supported = ", ".join(sorted(LOADER_REGISTRY.keys()))
        raise ValueError(f"No loader found for extension '{ext}'. Supported: {supported}")
    return cls()


__all__ = ["BaseLoader", "get_loader", "LOADER_REGISTRY"]
