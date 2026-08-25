"""Command-line tools for building and printing a flag-football playbook."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .language import PlaySyntaxError, parse_play
from .library import PlayLibrary
from .render import write_card, write_sheet
from .routes import DEFAULT_ROUTES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flag-play",
        description="Build 5v5 flag-football play cards from compact route codes",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    card = commands.add_parser("card", help="render one play card")
    card.add_argument("play", help='for example: "1445 | Four Strong | spread"')
    card.add_argument("-o", "--output", type=Path, required=True)

    add = commands.add_parser("add", help="add a play to a JSON playbook")
    add.add_argument("playbook", type=Path)
    add.add_argument("play", help='for example: "1445 | Four Strong | spread | Read 2 first"')
    add.add_argument("--tag", action="append", default=[])

    show = commands.add_parser("list", help="list plays in a JSON playbook")
    show.add_argument("playbook", type=Path)

    sheet = commands.add_parser("sheet", help="render a nine-card printable sheet")
    sheet.add_argument("playbook", type=Path)
    sheet.add_argument("-o", "--output", type=Path, required=True)
    sheet.add_argument("--start", type=int, default=1, help="first play number (default: 1)")

    commands.add_parser("routes", help="show the default route tree")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "card":
            play = parse_play(args.play)
            write_card(play, args.output)
            print(f"Wrote {args.output}")
        elif args.command == "add":
            library = (
                PlayLibrary.load(args.playbook)
                if args.playbook.exists()
                else PlayLibrary()
            )
            parsed = parse_play(args.play)
            play = type(parsed)(
                routes=parsed.routes,
                name=parsed.name,
                formation=parsed.formation,
                notes=parsed.notes,
                tags=tuple(args.tag),
            )
            library.add(play)
            library.save(args.playbook)
            print(f"Added {play.code} {play.name}".rstrip())
        elif args.command == "list":
            for index, play in enumerate(PlayLibrary.load(args.playbook), start=1):
                print(f"{index:>2}. {play.code}  {play.name or '(unnamed)'}  [{play.formation}]")
        elif args.command == "sheet":
            if args.start < 1:
                raise ValueError("--start must be at least 1")
            plays = list(PlayLibrary.load(args.playbook))
            selected = plays[args.start - 1 : args.start + 8]
            if not selected:
                raise ValueError("the selected sheet does not contain any plays")
            write_sheet(selected, args.output)
            print(f"Wrote {len(selected)} play(s) to {args.output}")
        elif args.command == "routes":
            for number, route in DEFAULT_ROUTES.items():
                print(f"{number}: {route.name:<9} {route.description}")
    except (OSError, ValueError, PlaySyntaxError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0
