"""Default route tree and formations.

Teams use different numbering systems. The renderer accepts any route mapping,
so applications can replace this tree without changing the play language.
"""

from __future__ import annotations

from .models import Formation, Point, Route


def _points(*values: tuple[float, float]) -> tuple[Point, ...]:
    return tuple(Point(x, y) for x, y in values)


DEFAULT_ROUTES: dict[int, Route] = {
    0: Route(0, "Hitch", _points((0.00, 0.27), (0.00, 0.38), (0.00, 0.31)), "Quick hitch"),
    1: Route(1, "Slant", _points((0.00, 0.12), (0.20, 0.37)), "Quick inside slant"),
    2: Route(2, "Out", _points((0.00, 0.27), (-0.22, 0.27)), "Speed out"),
    3: Route(3, "Dig", _points((0.00, 0.42), (0.25, 0.42)), "Inside dig"),
    4: Route(
        4,
        "Curl",
        _points((0.00, 0.48), (0.00, 0.55), (0.08, 0.46)),
        "Curl back toward the quarterback",
    ),
    5: Route(
        5,
        "Comeback",
        _points((0.00, 0.55), (-0.08, 0.65), (-0.17, 0.48)),
        "Outside comeback",
    ),
    6: Route(6, "Corner", _points((0.00, 0.36), (-0.24, 0.72)), "Corner route"),
    7: Route(7, "Post", _points((0.00, 0.36), (0.23, 0.74)), "Post route"),
    8: Route(8, "Go", _points((0.00, 0.78)), "Straight go route"),
    9: Route(
        9,
        "Wheel",
        _points((-0.13, 0.13), (-0.17, 0.30), (-0.13, 0.62)),
        "Outside wheel route",
    ),
}


DEFAULT_FORMATIONS: dict[str, Formation] = {
    "spread": Formation("spread", (0.12, 0.38, 0.62, 0.88)),
    "bunch-left": Formation("bunch-left", (0.14, 0.27, 0.40, 0.86)),
    "bunch-right": Formation("bunch-right", (0.14, 0.60, 0.73, 0.86)),
    "trips-left": Formation("trips-left", (0.10, 0.28, 0.46, 0.86)),
    "trips-right": Formation("trips-right", (0.14, 0.54, 0.72, 0.90)),
}
