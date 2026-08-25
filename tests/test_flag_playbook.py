from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from flag_playbook import Play, PlayLibrary, PlaySyntaxError, parse_play
from flag_playbook.render import render_card_svg, render_sheet_svg


class PlayLanguageTests(unittest.TestCase):
    def test_four_digits_map_left_to_right(self) -> None:
        play = parse_play("1445")

        self.assertEqual(play.routes, (1, 4, 4, 5))
        self.assertEqual(play.code, "1445")
        self.assertEqual(play.formation, "spread")

    def test_separators_and_metadata_are_supported(self) -> None:
        play = parse_play("1-4-4-5 | Four Strong | bunch-right | Read the slant")

        self.assertEqual(play.name, "Four Strong")
        self.assertEqual(play.formation, "bunch-right")
        self.assertEqual(play.notes, "Read the slant")

    def test_invalid_route_count_has_helpful_error(self) -> None:
        with self.assertRaisesRegex(PlaySyntaxError, "exactly four digits"):
            parse_play("145")


class PlayLibraryTests(unittest.TestCase):
    def test_json_round_trip_and_search(self) -> None:
        original = PlayLibrary(
            [
                Play((1, 4, 4, 5), "Four Strong", tags=("red-zone",)),
                Play((8, 2, 3, 8), "Clear Out", formation="trips-left"),
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plays.json"
            original.save(path)
            restored = PlayLibrary.load(path)

        self.assertEqual(len(restored), 2)
        self.assertEqual(restored.find("clear")[0].code, "8238")
        self.assertEqual(restored.find(tag="red-zone")[0].name, "Four Strong")

    def test_rejects_invalid_document_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plays.json"
            path.write_text(json.dumps([]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "plays list"):
                PlayLibrary.load(path)


class RenderingTests(unittest.TestCase):
    def test_card_contains_routes_and_player_labels(self) -> None:
        svg = render_card_svg(parse_play("1445 | Four & Strong"))

        self.assertIn("Four &amp; Strong", svg)
        self.assertEqual(svg.count('class="route"'), 4)
        self.assertIn(">1</text>", svg)
        self.assertIn(">Q</text>", svg)

    def test_sheet_accepts_nine_plays(self) -> None:
        svg = render_sheet_svg([parse_play("1445")] * 9)

        self.assertEqual(svg.count('class="card"'), 9)

    def test_sheet_rejects_more_than_nine_plays(self) -> None:
        with self.assertRaisesRegex(ValueError, "at most nine"):
            render_sheet_svg([parse_play("1445")] * 10)

    def test_unknown_formation_is_reported(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown formation"):
            render_card_svg(parse_play("1445 | Name | wishbone"))


if __name__ == "__main__":
    unittest.main()
