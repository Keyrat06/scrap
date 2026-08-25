"""Dependency-free SVG rendering for play cards and printable bracelet sheets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
from pathlib import Path

from .models import Formation, Play, Route
from .routes import DEFAULT_FORMATIONS, DEFAULT_ROUTES

CARD_WIDTH = 162  # 2.25 inches at 72 points per inch
CARD_HEIGHT = 252  # 3.5 inches


def render_card_svg(
    play: Play,
    *,
    routes: Mapping[int, Route] = DEFAULT_ROUTES,
    formations: Mapping[str, Formation] = DEFAULT_FORMATIONS,
) -> str:
    """Render one bracelet-sized play card as SVG."""

    body = _card_group(play, routes=routes, formations=formations)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="2.25in" height="3.5in" '
        f'viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}">\n'
        f"{_styles()}\n{_arrow_marker()}\n{body}\n</svg>\n"
    )


def render_sheet_svg(
    plays: Sequence[Play],
    *,
    routes: Mapping[int, Route] = DEFAULT_ROUTES,
    formations: Mapping[str, Formation] = DEFAULT_FORMATIONS,
) -> str:
    """Render up to nine plays on a US Letter cut sheet."""

    if not plays:
        raise ValueError("at least one play is required")
    if len(plays) > 9:
        raise ValueError("a bracelet sheet holds at most nine plays")

    page_width, page_height = 612, 792
    gap = 9
    left = (page_width - (3 * CARD_WIDTH + 2 * gap)) / 2
    top = (page_height - (3 * CARD_HEIGHT + 2 * gap)) / 2
    cards = []
    for index, play in enumerate(plays):
        x = left + (index % 3) * (CARD_WIDTH + gap)
        y = top + (index // 3) * (CARD_HEIGHT + gap)
        cards.append(
            f'<g transform="translate({x:g} {y:g})">'
            f"{_card_group(play, routes=routes, formations=formations)}</g>"
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" '
        f'viewBox="0 0 {page_width} {page_height}">\n'
        f"{_styles()}\n{_arrow_marker()}\n"
        '<rect width="100%" height="100%" fill="white"/>\n'
        + "\n".join(cards)
        + "\n</svg>\n"
    )


def write_card(play: Play, destination: str | Path) -> None:
    _write(destination, render_card_svg(play))


def write_sheet(plays: Sequence[Play], destination: str | Path) -> None:
    _write(destination, render_sheet_svg(plays))


def _write(destination: str | Path, content: str) -> None:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _card_group(
    play: Play,
    *,
    routes: Mapping[int, Route],
    formations: Mapping[str, Formation],
) -> str:
    try:
        formation = formations[play.formation]
    except KeyError as error:
        choices = ", ".join(sorted(formations))
        raise ValueError(f"unknown formation {play.formation!r}; choose from {choices}") from error
    missing = [number for number in play.routes if number not in routes]
    if missing:
        raise ValueError(f"route tree has no definition for route {missing[0]}")

    field_x, field_y, field_width, field_height = 8, 37, 146, 177
    line_y = field_y + field_height * 0.87
    elements = [
        f'<rect class="card" width="{CARD_WIDTH}" height="{CARD_HEIGHT}"/>',
        '<path class="cut" d="M0 8V0H8 M154 0H162V8 M162 244V252H154 M8 252H0V244"/>',
        f'<text class="title" x="8" y="16">{escape(play.name or "PLAY")}</text>',
        f'<text class="code" x="154" y="17" text-anchor="end">{play.code}</text>',
        f'<text class="formation" x="8" y="29">{escape(play.formation.upper())}</text>',
        f'<rect class="field" x="{field_x}" y="{field_y}" '
        f'width="{field_width}" height="{field_height}"/>',
        f'<line class="yard" x1="{field_x}" y1="{line_y:g}" '
        f'x2="{field_x + field_width}" y2="{line_y:g}"/>',
    ]
    for fraction in (0.2, 0.4, 0.6, 0.8):
        y = field_y + field_height * fraction
        elements.append(
            f'<line class="hash" x1="{field_x}" y1="{y:g}" '
            f'x2="{field_x + field_width}" y2="{y:g}"/>'
        )

    for index, (start, number) in enumerate(zip(formation.receiver_x, play.routes)):
        route = routes[number]
        start_x = field_x + start * field_width
        inside_sign = 1 if start < 0.5 else -1
        points = [(start_x, line_y)]
        points.extend(
            (
                start_x + point.x * field_width * inside_sign,
                line_y - point.y * field_height,
            )
            for point in route.path
        )
        encoded = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        elements.extend(
            [
                f'<polyline class="route" points="{encoded}" marker-end="url(#arrow)"/>',
                f'<circle class="receiver" cx="{start_x:.1f}" cy="{line_y:.1f}" r="5"/>',
                f'<text class="player" x="{start_x:.1f}" y="{line_y + 2.4:.1f}" '
                f'text-anchor="middle">{index + 1}</text>',
            ]
        )

    qb_x = field_x + field_width / 2
    qb_y = field_y + field_height * 0.96
    elements.extend(
        [
            f'<circle class="qb" cx="{qb_x:g}" cy="{qb_y:g}" r="5"/>',
            f'<text class="player inverse" x="{qb_x:g}" y="{qb_y + 2.4:g}" '
            'text-anchor="middle">Q</text>',
        ]
    )
    route_names = " · ".join(
        f"{index + 1}:{routes[number].name}"
        for index, number in enumerate(play.routes)
    )
    footer = play.notes or route_names
    if len(footer) > 44:
        footer = footer[:41].rstrip() + "..."
    elements.append(f'<text class="notes" x="81" y="229" text-anchor="middle">{escape(footer)}</text>')
    if play.notes:
        elements.append(
            f'<text class="legend" x="81" y="241" text-anchor="middle">'
            f"{escape(route_names)}</text>"
        )
    return "\n".join(elements)


def _styles() -> str:
    return """<style>
.card{fill:#fff;stroke:#111;stroke-width:1}.cut{fill:none;stroke:#777;stroke-width:.5}
.field{fill:#f8faf7;stroke:#647067;stroke-width:.7}.yard{stroke:#59655d;stroke-width:1}
.hash{stroke:#c8cec9;stroke-width:.45;stroke-dasharray:2 2}
.route{fill:none;stroke:#111;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.receiver{fill:#fff;stroke:#111;stroke-width:1.2}.qb{fill:#111}
text{font-family:Arial,sans-serif;fill:#111}.title{font-size:10px;font-weight:700}
.code{font-size:15px;font-weight:800;letter-spacing:1px}.formation{font-size:5.5px;letter-spacing:.8px}
.player{font-size:5px;font-weight:700}.inverse{fill:#fff}.notes{font-size:6px;font-weight:700}
.legend{font-size:4.8px;fill:#414141}
</style>"""


def _arrow_marker() -> str:
    return (
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
        '<path d="M0 0L10 5L0 10z" fill="#111"/></marker></defs>'
    )
