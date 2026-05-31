"""Tests for DataMap core — DataAnalyzer and tree building."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from datamap.core import DataAnalyzer, DataMapError, DataNode

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def json_file(tmp_path: Path) -> Path:
    data = {
        "name": "DataMap",
        "version": 1,
        "active": True,
        "tags": ["cli", "python", "rich"],
        "meta": {"author": "dev", "stars": 5000},
        "nothing": None,
    }
    p = tmp_path / "sample.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


@pytest.fixture()
def bad_json_file(tmp_path: Path) -> Path:
    p = tmp_path / "bad.json"
    p.write_text("{invalid json", encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# DataNode
# ---------------------------------------------------------------------------


class TestDataNode:
    def test_type_str(self):
        n = DataNode(value="hello")
        assert n.python_type == "str"

    def test_type_int(self):
        assert DataNode(value=42).python_type == "int"

    def test_type_float(self):
        assert DataNode(value=3.14).python_type == "float"

    def test_type_bool(self):
        assert DataNode(value=True).python_type == "bool"

    def test_type_null(self):
        assert DataNode(value=None).python_type == "null"

    def test_type_list(self):
        assert DataNode(value=[1, 2]).python_type == "list"

    def test_type_dict(self):
        assert DataNode(value={"a": 1}).python_type == "dict"


# ---------------------------------------------------------------------------
# DataAnalyzer — load
# ---------------------------------------------------------------------------


class TestDataAnalyzerLoad:
    def test_load_json(self, json_file: Path):
        a = DataAnalyzer(json_file)
        data = a.load()
        assert data["name"] == "DataMap"
        assert data["version"] == 1
        assert data["tags"] == ["cli", "python", "rich"]

    def test_load_missing_file(self, tmp_path: Path):
        a = DataAnalyzer(tmp_path / "ghost.json")
        with pytest.raises(DataMapError, match="No loader|not found"):
            a.load()

    def test_load_invalid_json(self, bad_json_file: Path):
        a = DataAnalyzer(bad_json_file)
        with pytest.raises(DataMapError, match="Invalid JSON"):
            a.load()

    def test_file_size_populated(self, json_file: Path):
        a = DataAnalyzer(json_file)
        a.load()
        assert a._file_size > 0


# ---------------------------------------------------------------------------
# DataAnalyzer — analyse
# ---------------------------------------------------------------------------


class TestDataAnalyzerAnalyse:
    def test_dict_children(self, json_file: Path):
        a = DataAnalyzer(json_file)
        data = a.load()
        root = a.analyse(data)
        assert root.python_type == "dict"
        assert root.length == 6
        assert len(root.children) == 6

    def test_list_children(self, json_file: Path):
        a = DataAnalyzer(json_file)
        data = a.load()
        root = a.analyse(data)
        tags_node = next(c for c in root.children if getattr(c, "_key", "") == "tags")
        assert tags_node.python_type == "list"
        assert tags_node.length == 3

    def test_nested_dict(self, json_file: Path):
        a = DataAnalyzer(json_file)
        data = a.load()
        root = a.analyse(data)
        meta_node = next(c for c in root.children if getattr(c, "_key", "") == "meta")
        assert meta_node.python_type == "dict"
        assert meta_node.length == 2

    def test_null_node(self, json_file: Path):
        a = DataAnalyzer(json_file)
        data = a.load()
        root = a.analyse(data)
        null_node = next(c for c in root.children if getattr(c, "_key", "") == "nothing")
        assert null_node.python_type == "null"

    def test_max_depth_limits_children(self, json_file: Path):
        a = DataAnalyzer(json_file, max_depth=0)
        data = a.load()
        root = a.analyse(data)
        # With depth=0, root is a dict but children should not be expanded
        assert all(len(c.children) == 0 for c in root.children)

    def test_str_length(self):
        a = DataAnalyzer.__new__(DataAnalyzer)
        node = a.analyse("hello world")
        assert node.length == 11


# ---------------------------------------------------------------------------
# DataAnalyzer — build_tree (smoke test — just check it doesn't crash)
# ---------------------------------------------------------------------------


class TestBuildTree:
    def test_returns_rich_tree(self, json_file: Path):
        from rich.tree import Tree

        a = DataAnalyzer(json_file)
        data = a.load()
        root_node = a.analyse(data)
        tree = a.build_tree(root_node, label="test")
        assert isinstance(tree, Tree)

    def test_render_no_error(self, json_file: Path):
        from rich.console import Console

        console = Console(record=True, width=120)
        a = DataAnalyzer(json_file)
        a.render(console=console)
        output = console.export_text()
        assert "DataMap" in output or "name" in output
