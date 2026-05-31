"""
DataMap Core — DataAnalyzer class + Rich tree renderer.

This module is the heart of DataMap.  It:
  - Loads any supported file via the pluggable loader system.
  - Recursively traverses the data.
  - Annotates every node with its Python type, length/key-count metadata.
  - Renders the result as a colour-coded Rich tree.
  - Exposes a small ``__main__``-style CLI when run directly.

CLI usage (via pyproject entry-point):
    datamap <path_to_file> [--depth N] [--no-meta]
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

# ---------------------------------------------------------------------------
# Public exception
# ---------------------------------------------------------------------------


class DataMapError(Exception):
    """Top-level exception for all DataMap failures."""


# ---------------------------------------------------------------------------
# Palette (single source-of-truth for colours)
# ---------------------------------------------------------------------------

_C = {
    "key":      "bold cyan",
    "str":      "green",
    "number":   "gold1",
    "bool":     "medium_purple1",
    "null":     "dim red",
    "type":     "grey50",
    "meta":     "grey46",
    "list":     "bold yellow",
    "dict":     "bold cyan",
    "logo":     "bold bright_cyan",
}

ASCII_LOGO = (
    "[bold bright_cyan]"
    "\n"
    "  ____        _        __  __\n"
    " |  _ \\  __ _| |_ __ _|  \\/  | __ _ _ __\n"
    " | | | |/ _` | __/ _` | |\\/| |/ _` | '_ \\\n"
    " | |_| | (_| | || (_| | |  | | (_| | |_) |\n"
    " |____/ \\__,_|\\__\\__,_|_|  |_|\\__,_| .__/\n"
    "                                     |_|   \n"
    "[/bold bright_cyan]"
    "[grey50]  visualize any data  *  JSON  *  YAML  *  TOML  *  .env[/grey50]\n"
)


# ---------------------------------------------------------------------------
# DataNode — internal representation of a single tree node
# ---------------------------------------------------------------------------


@dataclass
class DataNode:
    """Holds a value and its analysed metadata."""

    value: Any
    python_type: str = field(default="")
    length: Optional[int] = None        # len() for list/dict/str
    children: List["DataNode"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.python_type = self._detect_type(self.value)

    @staticmethod
    def _detect_type(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "str"
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "dict"
        return type(value).__name__


# ---------------------------------------------------------------------------
# DataAnalyzer
# ---------------------------------------------------------------------------


class DataAnalyzer:
    """
    Анализирует файл данных и создает визуализацию в виде дерева Rich Tree.

    Параметры
    ----------
    path:
        Путь к файлу для анализа.
    max_depth:
        Максимальная глубина рекурсии (``None`` = без ограничений).
    show_meta:
        Нужно ли отображать метаданные (кол-во ключей/элементов) для коллекций.
    """

    def __init__(
        self,
        path: Path,
        *,
        max_depth: Optional[int] = None,
        show_meta: bool = True,
    ) -> None:
        self.path = Path(path)
        self.max_depth = max_depth
        self.show_meta = show_meta
        self._file_size: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> Any:
        """Load *self.path* via the appropriate loader and return raw data."""
        from datamap.loaders import get_loader

        loader = get_loader(self.path)
        try:
            data = loader.load(self.path)
        except (FileNotFoundError, PermissionError, ValueError) as exc:
            raise DataMapError(str(exc)) from exc

        try:
            self._file_size = self.path.stat().st_size
        except OSError:
            self._file_size = 0

        return data

    def analyse(self, data: Any) -> DataNode:
        """Recursively build a :class:`DataNode` tree from *data*."""
        return self._visit(data, depth=0)

    def build_tree(self, root_node: DataNode, label: str = "") -> Tree:
        """Convert a :class:`DataNode` tree into a Rich :class:`Tree`."""
        root_label = self._format_root_label(label)
        tree = Tree(root_label)
        self._attach_children(tree, root_node, depth=0)
        return tree

    def render(self, console: Optional[Console] = None) -> None:
        """Full pipeline: load -> analyse -> render to *console*."""
        console = console or Console()
        console.print(ASCII_LOGO)

        data = self.load()
        root_node = self.analyse(data)
        meta = self._file_meta_line()
        tree = self.build_tree(root_node, label=self.path.name)

        console.print(
            Panel(
                tree,
                title=f"[bold]{self.path.name}[/bold]",
                subtitle=meta,
                border_style="cyan",
                box=box.ROUNDED,
            )
        )

    # ------------------------------------------------------------------
    # Internal helpers — traversal
    # ------------------------------------------------------------------

    def _visit(self, value: Any, depth: int) -> DataNode:
        node = DataNode(value=value)

        if isinstance(value, dict):
            node.length = len(value)
            if self.max_depth is None or depth < self.max_depth:
                for k, v in value.items():
                    child = self._visit(v, depth + 1)
                    child._key = str(k)  # type: ignore[attr-defined]
                    node.children.append(child)

        elif isinstance(value, list):
            node.length = len(value)
            if self.max_depth is None or depth < self.max_depth:
                for i, item in enumerate(value):
                    child = self._visit(item, depth + 1)
                    child._key = str(i)  # type: ignore[attr-defined]
                    node.children.append(child)

        elif isinstance(value, str):
            node.length = len(value)

        return node

    # ------------------------------------------------------------------
    # Internal helpers — rendering
    # ------------------------------------------------------------------

    def _format_root_label(self, label: str) -> Text:
        t = Text()
        t.append(label or str(self.path), style="bold bright_white")
        return t

    def _attach_children(
        self, parent: Tree, node: DataNode, depth: int
    ) -> None:
        for child in node.children:
            key = getattr(child, "_key", "?")
            branch_label = self._make_label(key, child)
            branch = parent.add(branch_label)
            if child.children:
                self._attach_children(branch, child, depth + 1)

    def _make_label(self, key: str, node: DataNode) -> Text:
        t = Text()
        # key
        t.append(key, style=_C["key"])
        t.append(": ", style="dim")

        vtype = node.python_type

        if vtype == "dict":
            count = node.length or 0
            t.append("{...}", style=_C["dict"])
            if self.show_meta:
                t.append(f"  [{count} keys]", style=_C["meta"])

        elif vtype == "list":
            count = node.length or 0
            t.append("[...]", style=_C["list"])
            if self.show_meta:
                t.append(f"  [{count} items]", style=_C["meta"])

        elif vtype == "null":
            t.append("null", style=_C["null"])
            t.append("  [null]", style=_C["type"])

        elif vtype == "bool":
            t.append(str(node.value), style=_C["bool"])
            t.append("  [bool]", style=_C["type"])

        elif vtype in ("int", "float"):
            t.append(str(node.value), style=_C["number"])
            t.append(f"  [{vtype}]", style=_C["type"])

        elif vtype == "str":
            display = str(node.value)
            if len(display) > 120:
                display = display[:117] + "..."
            t.append(f'"{display}"', style=_C["str"])
            if self.show_meta and (node.length or 0) > 0:
                t.append(f"  [str.{node.length}]", style=_C["type"])
            else:
                t.append("  [str]", style=_C["type"])

        else:
            t.append(repr(node.value), style="white")
            t.append(f"  [{vtype}]", style=_C["type"])

        return t

    def _file_meta_line(self) -> str:
        size = self._file_size
        if size < 1024:
            human = f"{size} B"
        elif size < 1024 ** 2:
            human = f"{size / 1024:.1f} KB"
        else:
            human = f"{size / 1024**2:.1f} MB"
        return f"[grey50]{self.path}  |  {human}[/grey50]"


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


_SUBCOMMANDS = {"view", "export", "tui", "info"}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="datamap",
        description="Visualize JSON, YAML, TOML, or .env data as a Rich tree.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  datamap config.json\n"
            "  datamap settings.yaml --depth 3\n"
            "  datamap pyproject.toml --no-meta\n"
            "  datamap .env\n"
            "  datamap export config.json --format svg\n"
            "  datamap tui config.json\n"
            "  datamap info\n"
        ),
    )
    sub = p.add_subparsers(dest="command")

    # ---- view (default) ----
    view = sub.add_parser("view", help="Render a file as a tree (default)")
    view.add_argument("file", type=Path, metavar="FILE")
    view.add_argument(
        "--depth", "-d", type=int, default=None, metavar="N",
        help="Maximum depth to expand (default: unlimited)"
    )
    view.add_argument(
        "--no-meta", action="store_true",
        help="Hide length/key-count metadata"
    )

    # ---- export ----
    export_p = sub.add_parser("export", help="Export tree as SVG or HTML")
    export_p.add_argument("file", type=Path, metavar="FILE")
    export_p.add_argument(
        "--format", choices=["svg", "html"], default="svg",
        help="Output format (default: svg)"
    )
    export_p.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Output file path (default: <FILE>.<format>)"
    )
    export_p.add_argument(
        "--depth", "-d", type=int, default=None, metavar="N"
    )

    # ---- tui ----
    tui_p = sub.add_parser("tui", help="Open the interactive Terminal UI")
    tui_p.add_argument(
        "file", nargs="?", type=Path, metavar="FILE",
        help="File to open in TUI (optional)"
    )

    # ---- info ----
    sub.add_parser("info", help="Show registered loaders")

    return p


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry-point — returns exit code."""
    # ----------------------------------------------------------------
    # Positional shortcut: `datamap <file> [opts]`
    # If the first non-flag token is not a known subcommand, inject
    # 'view' so argparse routes it correctly.
    # ----------------------------------------------------------------
    if argv is None:
        argv = sys.argv[1:]

    # Find first non-flag token
    first_positional: Optional[str] = None
    for tok in argv:
        if not tok.startswith("-"):
            first_positional = tok
            break

    if first_positional is not None and first_positional not in _SUBCOMMANDS:
        argv = ["view"] + list(argv)

    parser = _build_parser()
    args = parser.parse_args(argv)
    console = Console()

    # ---- info ----
    if args.command == "info":
        from datamap.loaders import LOADER_REGISTRY
        console.print("[bold cyan]Registered DataMap loaders:[/bold cyan]")
        for ext, cls in sorted(LOADER_REGISTRY.items()):
            console.print(f"  [green]{ext}[/green]  ->  {cls.__name__}")
        return 0

    # ---- tui ----
    if args.command == "tui":
        try:
            from datamap.app import DataMapApp
        except ImportError as exc:
            console.print(f"[red]TUI requires Textual:[/red]  pip install textual\n{exc}")
            return 1
        tui_file = getattr(args, "file", None)
        DataMapApp(tui_file).run()
        return 0

    # ---- export ----
    if args.command == "export":
        try:
            from datamap.export import export_tree
        except ImportError as exc:
            console.print(f"[red]Export error:[/red] {exc}")
            return 1
        try:
            out = export_tree(
                args.file,
                fmt=args.format,
                output=args.output,
                max_depth=args.depth,
            )
            console.print(f"[green][OK] Exported:[/green] {out}")
        except DataMapError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            return 1
        return 0

    # ---- view (default / positional) ----
    if args.command == "view":
        try:
            analyzer = DataAnalyzer(
                args.file,
                max_depth=args.depth,
                show_meta=not args.no_meta,
            )
            analyzer.render(console)
        except DataMapError as exc:
            console.print(f"[bold red]Error:[/bold red] {exc}")
            return 1
        return 0

    # No subcommand and no file -> show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
