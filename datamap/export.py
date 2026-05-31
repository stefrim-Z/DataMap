"""
DataMap Export — SVG and HTML export via Rich's record mode.

Usage:
    datamap export config.json --format svg
    datamap export settings.yaml --format html --output ./docs/tree.html
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console

from datamap.core import DataAnalyzer, DataMapError


def export_tree(
    path: Path,
    *,
    fmt: str = "svg",
    output: Optional[Path] = None,
    max_depth: Optional[int] = None,
) -> Path:
    """
    Экспортирует дерево визуализации в формат SVG или HTML.

    Параметры
    ----------
    path:      Входной файл с данными.
    fmt:       Формат экспорта (``"svg"`` или ``"html"``).
    output:    Путь к выходному файлу. По умолчанию: ``<имя_файла>.<формат>``.
    max_depth: Максимальная глубина дерева.

    Возвращает
    -------
    Path
        Абсолютный путь к созданному файлу.
    """
    path = Path(path)
    if fmt not in ("svg", "html"):
        raise ValueError(f"Unsupported export format: {fmt!r} (use 'svg' or 'html')")

    if output is None:
        output = path.with_suffix(f".{fmt}")
    output = Path(output)

    # Use a recording console — no actual terminal output
    record_console = Console(record=True, width=120)

    analyzer = DataAnalyzer(path, max_depth=max_depth, show_meta=True)
    try:
        analyzer.render(console=record_console)
    except DataMapError:
        raise

    output.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "svg":
        svg_content = record_console.export_svg(
            title=f"DataMap — {path.name}",
        )
        output.write_text(svg_content, encoding="utf-8")
    else:
        html_content = record_console.export_html(
            title=f"DataMap — {path.name}",
            inline_styles=True,
        )
        output.write_text(html_content, encoding="utf-8")

    return output.resolve()
