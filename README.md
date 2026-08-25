# Flag Football Playbook

A small, dependency-free Python library for turning 5v5 flag-football route
descriptions into play diagrams and printable wrist-bracelet cards.

## Quick start

Python 3.11 or newer is required.

```bash
python -m pip install -e .
flag-play card "1445 | Four Strong | spread | Read the slant first" \
  --output results/four-strong.svg
flag-play sheet examples/playbook.json --output results/bracelet-sheet.svg
```

Open the generated SVG in a browser and print it at 100% scale. A card is 2.25 by
3.5 inches; a US Letter sheet contains up to nine cut-out cards.

## Play language

The first four digits list receiver routes from left to right. In `1445`,
receiver 1 runs route 1, receivers 2 and 3 run route 4, and receiver 4 runs
route 5.

```bash
1445
1-4-4-5
1445 | Four Strong
1445 | Four Strong | spread
1445 | Four Strong | spread | Read the slant, then the curls
```

The optional sections are `NAME | FORMATION | NOTES`. Available formations are
`spread`, `bunch-left`, `bunch-right`, `trips-left`, and `trips-right`.

The default route tree is:

| Number | Route | Number | Route |
|---:|---|---:|---|
| 0 | Hitch | 5 | Comeback |
| 1 | Slant | 6 | Corner |
| 2 | Out | 7 | Post |
| 3 | Dig | 8 | Go |
| 4 | Curl | 9 | Wheel |

Route numbering is not universal. Applications can pass a custom mapping of
`Route` objects to the renderer while keeping the same four-digit language.

## Build a play library

```bash
flag-play add my-playbook.json \
  "1445 | Four Strong | spread | Read the slant first" --tag base
flag-play add my-playbook.json \
  "8238 | Clear Out | trips-left | Hit the dig" --tag third-down
flag-play list my-playbook.json
flag-play sheet my-playbook.json --output results/sheet.svg
flag-play routes
```

JSON playbooks are intentionally simple and portable. See
[`examples/playbook.json`](examples/playbook.json).

## Python API

```python
from flag_playbook import PlayLibrary, parse_play, write_card, write_sheet

play = parse_play("1445 | Four Strong | spread")
write_card(play, "results/four-strong.svg")

playbook = PlayLibrary([play, parse_play("8238 | Clear Out | trips-left")])
playbook.save("my-playbook.json")
write_sheet(list(playbook), "results/bracelet-sheet.svg")
```

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
