# news-image-20261117

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/Nughair/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/Nughair/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

One image that sums up the world news of **Tuesday 17 November 2026**, drawn as
a broadsheet front page. A masthead names the day; the hero panel shows the
U.S.–Iran war in the Strait of Hormuz, where tankers burned after striking
mines and U.S. warplanes hit Qeshm Island. Around it: the Shenzhen summit
bringing Xi, Trump and Putin together for a first three-way meeting; Ukraine's
strike on the Kerch Bridge as Russia hit Kyiv's bridges; the call to open
Gaza's crossings as winter rains flooded tents; the COP31 draft deal in
Antalya (fossil-fuel phase-out, $120bn climate finance); and Wall Street's
fall as Nvidia reported and U.S. AI-chip export rules tightened. A footer line
adds the U.S. losing its measles elimination status and India's one-wicket
U-19 Asia Cup final win over Pakistan.

The picture is drawn programmatically — `make_image.py` renders every panel
with Pillow from flat shapes, so all text is crisp — and committed as
`entry.png` (1024×1024). At grade time `main.ts` (Node 22, standard library
only) copies those bytes to `/output/entry.png`, identically on every run.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

To redraw the picture from source: `python3 make_image.py`.

---
<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
