"""Build an animated GIF summary from the benchmark PNG figures."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path, help="first PNG figure")
    parser.add_argument("second", type=Path, help="second PNG figure")
    parser.add_argument("output", type=Path, help="animated GIF destination")
    parser.add_argument("--transition-frames", type=int, default=8)
    parser.add_argument("--hold-ms", type=int, default=1800)
    parser.add_argument("--transition-ms", type=int, default=100)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.transition_frames < 1:
        raise ValueError("transition frames must be at least 1")

    first = Image.open(args.first).convert("RGB")
    second = Image.open(args.second).convert("RGB")
    if first.size != second.size:
        raise ValueError("input figures must have matching dimensions")

    forward = [
        Image.blend(first, second, step / args.transition_frames)
        for step in range(1, args.transition_frames)
    ]
    backward = [
        Image.blend(second, first, step / args.transition_frames)
        for step in range(1, args.transition_frames)
    ]
    frames = [first, *forward, second, *backward]
    durations = [
        args.hold_ms,
        *([args.transition_ms] * len(forward)),
        args.hold_ms,
        *([args.transition_ms] * len(backward)),
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
