"""
DataMap — Visualize any JSON/YAML/TOML/ENV data as a beautiful tree.
"""

__version__ = "1.0.0"
__author__ = "DataMap Contributors"
__license__ = "MIT"

from datamap.core import DataAnalyzer, DataMapError

__all__ = ["DataAnalyzer", "DataMapError", "__version__"]
