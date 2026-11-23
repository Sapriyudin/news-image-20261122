# The World in One Day — Sunday 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Sapriyudin/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Sapriyudin/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One image that sums up the world's news of **Sunday 22 November 2026**:
38 stories across 6 regions, 14 of them illustrated, on a single
newspaper front page. Lead story: **COP31 collapses in Antalya** — the
longest climate summit in history ends with no deal after the EU,
Britain and island states refuse a pact that never mentions fossil
fuels.

## How it works

`gen.py` draws the front page with PIL (DejaVu fonts, flat vector
illustrations, a numbered world map). `main.py` uses only the Python
standard library and copies the rendered `entry.png` to the output
directory, so the sandboxed run is deterministic — two runs write
byte-identical files.

```sh
python3 gen.py --variant A --out entry.png   # variant A: dense front page
python3 gen.py --variant B --out entry-b.png # variant B: visual-led
python3 main.py                              # writes out/entry.png
```

## Facts

- Every story was verified against live sources (Reuters, AP, CNN,
  BBC, The Times, WSJ) on Monday 23 November 2026. The disputed drone
  figure is settled from Ukraine's air force: **186 drones launched,
  161 downed** — not 400.
- Stories that happened on Saturday 21 November (EU–Indonesia trade
  deal, Chapo Isidro capture, BepiColombo, Saturday football) are
  labelled **SAT** / **FRI** in the image; everything else is 22 November.
- Image: 1024×1024 PNG, under 1 MiB, deterministic across runs.
  Variant A (this entry) is the dense front page; variant B is a
  visual-led layout with a wide lead panel and 31 stories.

## Bounty

Entry for [Sum up 22 November's world news in one image](https://make.fun/bounty/news-image-20261122)
on make.fun ($100, 50 places, deadline Tuesday 24 November 2026 07:00 WIB).
