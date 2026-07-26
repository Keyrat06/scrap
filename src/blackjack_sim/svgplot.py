"""Dependency-free SVG chart generation for experiment summaries."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .simulation import SimulationResult


def write_complexity_profitability_scatter(
    results: list[SimulationResult],
    destination: str | Path,
) -> None:
    if not results:
        raise ValueError("at least one result is required")

    width, height = 800, 500
    left, right, top, bottom = 90, 30, 45, 75
    plot_width = width - left - right
    plot_height = height - top - bottom
    x_values = [result.complexity for result in results]
    y_values = [result.profit_per_100_hands for result in results]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    y_min = min(y_min, 0.0)
    y_max = max(y_max, 0.0)
    if x_min == x_max:
        x_min, x_max = x_min - 1, x_max + 1
    if y_min == y_max:
        y_min, y_max = y_min - 1, y_max + 1
    y_padding = (y_max - y_min) * 0.12
    y_min -= y_padding
    y_max += y_padding

    def x_position(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_width

    def y_position(value: float) -> float:
        return top + (y_max - value) / (y_max - y_min) * plot_height

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        "<style>text{font-family:system-ui,sans-serif;fill:#222}"
        ".grid{stroke:#ddd;stroke-width:1}.axis{stroke:#333;stroke-width:2}"
        ".positive{fill:#198754}.negative{fill:#c0392b}</style>",
        f'<text x="{width / 2}" y="25" text-anchor="middle" font-size="18">'
        "Strategy complexity vs. profitability</text>",
    ]

    for step in range(6):
        value = y_min + (y_max - y_min) * step / 5
        y = y_position(value)
        elements.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}"/>')
        elements.append(
            f'<text x="{left-10}" y="{y+4:.2f}" text-anchor="end" font-size="12">{value:.2f}</text>'
        )

    zero_y = y_position(0)
    elements.extend(
        [
            f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}"/>',
            f'<line class="axis" x1="{left}" y1="{zero_y:.2f}" x2="{width-right}" y2="{zero_y:.2f}"/>',
            f'<text x="{width/2}" y="{height-20}" text-anchor="middle">'
            "Combined playing + betting complexity</text>",
            f'<text x="20" y="{height/2}" text-anchor="middle" '
            'transform="rotate(-90 20 250)">Profit per 100 hands (units)</text>',
        ]
    )

    ordered = sorted(results, key=lambda result: result.complexity)
    for result in ordered:
        x = x_position(result.complexity)
        y = y_position(result.profit_per_100_hands)
        point_class = "positive" if result.profit_per_100_hands >= 0 else "negative"
        elements.extend(
            [
                f'<circle class="{point_class}" cx="{x:.2f}" cy="{y:.2f}" r="6"/>',
                f'<text x="{x:.2f}" y="{height-bottom+20}" text-anchor="middle" '
                f'font-size="12">{result.complexity:g}</text>',
                f'<text x="{x+7:.2f}" y="{y-8:.2f}" font-size="12">'
                f"{escape(result.betting_strategy)} "
                f"({result.profit_per_100_hands:.2f})</text>",
            ]
        )
    elements.append("</svg>")

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(elements) + "\n", encoding="utf-8")


def write_betting_profitability_bars(
    results: list[SimulationResult],
    destination: str | Path,
) -> None:
    if not results:
        raise ValueError("at least one result is required")

    width, height = 800, 500
    left, right, top, bottom = 90, 30, 45, 105
    plot_width = width - left - right
    plot_height = height - top - bottom
    y_values = [result.profit_per_100_hands for result in results]
    y_min, y_max = min(min(y_values), 0.0), max(max(y_values), 0.0)
    if y_min == y_max:
        y_min, y_max = y_min - 1, y_max + 1
    padding = (y_max - y_min) * 0.12
    y_min -= padding
    y_max += padding

    def y_position(value: float) -> float:
        return top + (y_max - value) / (y_max - y_min) * plot_height

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        "<style>text{font-family:system-ui,sans-serif;fill:#222}"
        ".grid{stroke:#ddd;stroke-width:1}.axis{stroke:#333;stroke-width:2}"
        ".positive{fill:#198754}.negative{fill:#c0392b}</style>",
        f'<text x="{width/2}" y="25" text-anchor="middle" font-size="18">'
        "Profitability by betting policy</text>",
    ]
    for step in range(6):
        value = y_min + (y_max - y_min) * step / 5
        y = y_position(value)
        elements.append(
            f'<line class="grid" x1="{left}" y1="{y:.2f}" '
            f'x2="{width-right}" y2="{y:.2f}"/>'
        )
        elements.append(
            f'<text x="{left-10}" y="{y+4:.2f}" text-anchor="end" '
            f'font-size="12">{value:.2f}</text>'
        )

    zero_y = y_position(0)
    elements.extend(
        [
            f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" '
            f'y2="{height-bottom}"/>',
            f'<line class="axis" x1="{left}" y1="{zero_y:.2f}" '
            f'x2="{width-right}" y2="{zero_y:.2f}"/>',
            f'<text x="20" y="{height/2}" text-anchor="middle" '
            'transform="rotate(-90 20 250)">Profit per 100 hands (units)</text>',
        ]
    )

    slot_width = plot_width / len(results)
    bar_width = min(80.0, slot_width * 0.62)
    for index, result in enumerate(results):
        center = left + slot_width * (index + 0.5)
        value_y = y_position(result.profit_per_100_hands)
        bar_y = min(zero_y, value_y)
        bar_height = max(1.0, abs(value_y - zero_y))
        bar_class = "positive" if result.profit_per_100_hands >= 0 else "negative"
        elements.extend(
            [
                f'<rect class="{bar_class}" x="{center-bar_width/2:.2f}" '
                f'y="{bar_y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}"/>',
                f'<text x="{center:.2f}" y="{value_y-7 if result.profit_per_100_hands >= 0 else value_y+17:.2f}" '
                f'text-anchor="middle" font-size="12">{result.profit_per_100_hands:.2f}</text>',
                f'<text x="{center:.2f}" y="{height-bottom+20}" text-anchor="end" '
                f'font-size="12" transform="rotate(-25 {center:.2f} {height-bottom+20})">'
                f"{escape(result.betting_strategy)}</text>",
            ]
        )
    elements.append("</svg>")

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(elements) + "\n", encoding="utf-8")


def write_payout_complexity_plot(
    results: list[SimulationResult],
    destination: str | Path,
) -> None:
    """Backward-compatible alias for the complexity/profitability scatter plot."""
    write_complexity_profitability_scatter(results, destination)
