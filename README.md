# 22 November 2026 — 49 Stories, One Day

Entry for the [make.fun bounty news-image-20261122](https://make.fun/bounty/news-image-20261122):
sum up 22 November's world news in one image.

[![bounty](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/kamensr/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/kamensr/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

## The poster

`entry.png` (1024×1024) is a one-page newspaper for Sunday 22 November 2026:
49 stories across 7 regions — 4 illustrated features (COP31 collapses with no
deal; Russia's 186-drone overnight barrage on Ukraine; the Cikande candy-factory
fire in Indonesia; settler arson in the West Bank), 12 more stories in brief,
a UTC timeline, a world map with 11 numbered pins, 33 more one-liners, a DATE
CHECK box naming the near-miss stories that were *not* 22 November, and a
sources footer. Every story happened, or was first reported, on 22 November
2026 in some time zone; claims are labelled CLAIM vs CONFIRMED.

## How it is made

`generate.py` draws the poster with Pillow — flat illustration only (shapes,
panels, typography, simple drawn icons). No AI-generated imagery, no photo
collage, no external images.

`main.py` is the competition entrypoint: standard library only, it copies
`entry.png` to `$MAKEFUN_OUTPUT_DIR`. Deterministic — two runs produce
byte-identical output.

```
python3 generate.py   # redraw entry.png
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

## Licence

MIT — see `LICENSE`.
