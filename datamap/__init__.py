"""
DataMap — Визуализация данных (JSON/YAML/TOML/ENV) в виде красивого дерева в терминале.
"""

__version__ = "1.0.0"
__author__ = "DataMap Contributors"
__license__ = "MIT"

from datamap.core import DataAnalyzer, DataMapError

__all__ = ["DataAnalyzer", "DataMapError", "__version__"]
