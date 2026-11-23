# The Monday Ledger — news-image-20261123

Entry for the make.fun bounty: https://make.fun/bounty/news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Revaaa28/makefun-news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Revaaa28/makefun-news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

One page that sums up the world's news of **Monday 23 November 2026**:
36 stories, 7 regions, every one dated Monday 23 November 2026 or a Monday
development in a running story — the rising toll at Dymer as rescuers dig
through a flattened apartment block, the longest climate summit in history
ending in Antalya with no pact at all, and Asia's AI rout meeting rescue
funds and a soaring gold price — plus twelve pictured briefs, a dotted
world map whose pins match the story numbers, and a DATE CHECK box naming
the tempting stories that were *not* Monday's news.

## How it works

- `draw.py` renders `entry.png` (1024×1024) with Pillow, drawing at
  2048×2048 and downscaling with Lanczos (2× supersampling) so the small
  type stays clean. It is deterministic — seeded randomness only, no
  clock, no network — so two runs produce byte-identical output.
- `main.py` (Python 3.13, standard library only) copies the committed
  `entry.png` byte-for-byte to `$MAKEFUN_OUTPUT_DIR/entry.png` (default
  `/output`) and self-checks the copy's size.
- `news-notes.md` is the source trail: every story on the page with the
  outlet and wire it came from, including the refresh sweep that updated
  the Dymer toll to the primary Monday figures before the final render.

## Run

```sh
python3 draw.py   # regenerate entry.png
python3 main.py   # copy entry.png to the output dir
```
