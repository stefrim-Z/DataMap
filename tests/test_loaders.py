"""Tests for DataMap loaders."""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# JSON Loader
# ---------------------------------------------------------------------------


class TestJSONLoader:
    def test_load_valid(self, tmp_path: Path):
        from datamap.loaders.json_loader import JSONLoader

        p = tmp_path / "data.json"
        p.write_text('{"key": "value", "num": 42}', encoding="utf-8")
        result = JSONLoader().load(p)
        assert result == {"key": "value", "num": 42}

    def test_load_array(self, tmp_path: Path):
        from datamap.loaders.json_loader import JSONLoader

        p = tmp_path / "arr.json"
        p.write_text("[1, 2, 3]", encoding="utf-8")
        assert JSONLoader().load(p) == [1, 2, 3]

    def test_load_missing(self, tmp_path: Path):
        from datamap.loaders.json_loader import JSONLoader

        with pytest.raises(FileNotFoundError):
            JSONLoader().load(tmp_path / "ghost.json")

    def test_load_invalid_syntax(self, tmp_path: Path):
        from datamap.loaders.json_loader import JSONLoader

        p = tmp_path / "bad.json"
        p.write_text("{bad json", encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid JSON"):
            JSONLoader().load(p)

    def test_extensions(self):
        from datamap.loaders.json_loader import JSONLoader

        assert ".json" in JSONLoader.extensions


# ---------------------------------------------------------------------------
# YAML Loader
# ---------------------------------------------------------------------------


class TestYAMLLoader:
    def test_load_valid(self, tmp_path: Path):
        pytest.importorskip("yaml")
        from datamap.loaders.yaml_loader import YAMLLoader

        p = tmp_path / "data.yaml"
        p.write_text("key: value\nnum: 42\n", encoding="utf-8")
        result = YAMLLoader().load(p)
        assert result == {"key": "value", "num": 42}

    def test_load_missing(self, tmp_path: Path):
        pytest.importorskip("yaml")
        from datamap.loaders.yaml_loader import YAMLLoader

        with pytest.raises(FileNotFoundError):
            YAMLLoader().load(tmp_path / "ghost.yaml")

    def test_extensions(self):
        from datamap.loaders.yaml_loader import YAMLLoader

        assert ".yaml" in YAMLLoader.extensions
        assert ".yml" in YAMLLoader.extensions


# ---------------------------------------------------------------------------
# ENV Loader
# ---------------------------------------------------------------------------


class TestEnvLoader:
    def test_simple_pairs(self, tmp_path: Path):
        from datamap.loaders.env_loader import EnvLoader

        p = tmp_path / ".env"
        p.write_text("FOO=bar\nBAZ=123\n", encoding="utf-8")
        result = EnvLoader().load(p)
        assert result == {"FOO": "bar", "BAZ": "123"}

    def test_quoted_values(self, tmp_path: Path):
        from datamap.loaders.env_loader import EnvLoader

        p = tmp_path / ".env"
        p.write_text("KEY=\"hello world\"\nOTHER='single'\n", encoding="utf-8")
        result = EnvLoader().load(p)
        assert result["KEY"] == "hello world"
        assert result["OTHER"] == "single"

    def test_skips_comments(self, tmp_path: Path):
        from datamap.loaders.env_loader import EnvLoader

        p = tmp_path / ".env"
        p.write_text("# comment\nA=1\n", encoding="utf-8")
        result = EnvLoader().load(p)
        assert "comment" not in str(result)
        assert result["A"] == "1"

    def test_export_prefix(self, tmp_path: Path):
        from datamap.loaders.env_loader import EnvLoader

        p = tmp_path / ".env"
        p.write_text("export MY_VAR=hello\n", encoding="utf-8")
        assert EnvLoader().load(p)["MY_VAR"] == "hello"

    def test_extensions(self):
        from datamap.loaders.env_loader import EnvLoader

        assert ".env" in EnvLoader.extensions


# ---------------------------------------------------------------------------
# Loader registry auto-discovery
# ---------------------------------------------------------------------------


class TestLoaderRegistry:
    def test_json_registered(self):
        from datamap.loaders import LOADER_REGISTRY

        assert ".json" in LOADER_REGISTRY

    def test_yaml_registered(self):
        from datamap.loaders import LOADER_REGISTRY

        assert ".yaml" in LOADER_REGISTRY

    def test_env_registered(self):
        from datamap.loaders import LOADER_REGISTRY

        assert ".env" in LOADER_REGISTRY

    def test_get_loader_json(self, tmp_path: Path):
        from datamap.loaders import get_loader

        p = tmp_path / "x.json"
        loader = get_loader(p)
        assert ".json" in type(loader).extensions

    def test_get_loader_unknown_raises(self, tmp_path: Path):
        from datamap.loaders import get_loader

        with pytest.raises(ValueError, match="No loader"):
            get_loader(tmp_path / "x.xyz")
