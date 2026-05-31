"""
DataMap TUI — Textual-based interactive terminal UI.

Layout
------
┌─────────────────────────────────────────────────────────┐
│  Header: filename + hotkeys                              │
├────────────────────────┬────────────────────────────────│
│  [Search bar]          │                                 │
│  ────────────────────  │   Detail / Value pane          │
│  Tree  (left)          │   (syntax-highlighted JSON)    │
│                        │                                 │
├────────────────────────┴────────────────────────────────│
│  Footer: status                                          │
└─────────────────────────────────────────────────────────┘

Hotkeys
-------
  Arrow keys  Navigate tree
  C           Collapse all
  E           Expand  all
  F           Focus search bar
  Q / Ctrl-C  Quit
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    Static,
    Tree,
)
from textual.widgets.tree import TreeNode

from datamap.core import DataAnalyzer, DataMapError


# ---------------------------------------------------------------------------
# Helper — populate a Textual Tree from raw Python data
# ---------------------------------------------------------------------------


def _populate_node(node: TreeNode, value: Any, query: str = "") -> None:  # noqa: C901
    """Recursively attach children to *node* from *value*."""
    if isinstance(value, dict):
        for k, v in value.items():
            label = str(k)
            if query and query.lower() not in label.lower() and not _subtree_matches(v, query):
                continue
            child = node.add(label, data=v, expand=False)
            if isinstance(v, (dict, list)):
                _populate_node(child, v, query)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            label = f"[{i}]"
            if query and not _subtree_matches(v, query):
                continue
            child = node.add(label, data=v, expand=False)
            if isinstance(v, (dict, list)):
                _populate_node(child, v, query)


def _subtree_matches(value: Any, query: str) -> bool:
    """Return True if *query* appears anywhere inside *value* (fuzzy scan)."""
    if not query:
        return True
    q = query.lower()
    if isinstance(value, str):
        return q in value.lower()
    if isinstance(value, (int, float, bool)):
        return q in str(value).lower()
    if isinstance(value, dict):
        return any(
            q in str(k).lower() or _subtree_matches(v, query)
            for k, v in value.items()
        )
    if isinstance(value, list):
        return any(_subtree_matches(item, query) for item in value)
    return False


# ---------------------------------------------------------------------------
# Detail pane widget
# ---------------------------------------------------------------------------


class DetailPane(Static):
    """Right panel — shows the selected node's value as pretty JSON."""

    DEFAULT_CSS = """
    DetailPane {
        padding: 1 2;
        background: $surface;
        color: $text;
        overflow-y: auto;
    }
    """

    def show(self, value: Any) -> None:
        try:
            pretty = json.dumps(value, indent=2, ensure_ascii=False, default=str)
        except Exception:
            pretty = repr(value)
        self.update(pretty)


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------


class DataMapApp(App[None]):
    """Interactive Textual TUI for DataMap."""

    CSS_PATH = None  # inline CSS below
    TITLE = "DataMap"
    SUB_TITLE = "Interactive Data Explorer"

    BINDINGS = [
        Binding("q,ctrl+c", "quit", "Quit", show=True),
        Binding("c", "collapse_all", "Collapse All", show=True),
        Binding("e", "expand_all", "Expand All", show=True),
        Binding("f", "focus_search", "Search", show=True),
    ]

    DEFAULT_CSS = """
    Screen {
        background: $background;
    }
    #search-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        background: $panel;
        border-bottom: solid $primary;
    }
    #main-area {
        height: 1fr;
    }
    #tree-pane {
        width: 1fr;
        border-right: solid $primary;
        background: $surface;
        overflow-y: auto;
    }
    #detail-pane {
        width: 2fr;
        background: $surface-darken-1;
        overflow-y: auto;
    }
    #status-label {
        dock: bottom;
        height: 1;
        background: $primary-darken-2;
        color: $text-muted;
        padding: 0 1;
    }
    Input {
        border: none;
        background: transparent;
    }
    """

    # reactive: current search query
    search_query: reactive[str] = reactive("", layout=True)

    def __init__(self, path: Optional[Path] = None) -> None:
        super().__init__()
        self._path = Path(path) if path else None
        self._raw_data: Any = None

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            with Horizontal(id="search-bar"):
                yield Input(placeholder="🔍  Type to filter tree…", id="search-input")
            with Horizontal(id="main-area"):
                with Vertical(id="tree-pane"):
                    yield Tree("Loading…", id="data-tree")
                with Vertical(id="detail-pane"):
                    yield DetailPane("Select a node to inspect its value.", id="detail")
            yield Label("Ready", id="status-label")
        yield Footer()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        if self._path:
            self._load_file(self._path)
        else:
            self._set_status("[yellow]No file specified.  Pass a path as argument.[/yellow]")

    @work(thread=True)
    def _load_file(self, path: Path) -> None:
        """Background worker — load + analyse data without blocking the UI."""
        self._set_status(f"Loading {path.name}…")
        try:
            analyzer = DataAnalyzer(path, show_meta=True)
            data = analyzer.load()
            self._raw_data = data
            self.call_from_thread(self._populate_tree, data, "")
            self.call_from_thread(
                self._set_status, f"✔  {path.name}  —  loaded"
            )
        except DataMapError as exc:
            self.call_from_thread(
                self._set_status, f"[red]Error: {exc}[/red]"
            )

    def _populate_tree(self, data: Any, query: str) -> None:
        tree: Tree = self.query_one("#data-tree", Tree)
        tree.clear()
        label = str(self._path.name) if self._path else "data"
        root = tree.root
        root.set_label(label)
        _populate_node(root, data, query)
        root.expand()

    def _set_status(self, msg: str) -> None:
        self.query_one("#status-label", Label).update(msg)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    @on(Input.Changed, "#search-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        q = event.value.strip()
        if self._raw_data is not None:
            self._populate_tree(self._raw_data, q)

    @on(Tree.NodeSelected, "#data-tree")
    def on_node_selected(self, event: Tree.NodeSelected) -> None:
        detail: DetailPane = self.query_one("#detail", DetailPane)
        data = event.node.data
        if data is not None:
            detail.show(data)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_collapse_all(self) -> None:
        tree: Tree = self.query_one("#data-tree", Tree)
        tree.root.collapse_all()

    def action_expand_all(self) -> None:
        tree: Tree = self.query_one("#data-tree", Tree)
        tree.root.expand_all()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()
