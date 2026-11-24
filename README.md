# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/mellow-gecko-44/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/mellow-gecko-44/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

**The World in One Picture — Tuesday 24 November 2026.** An entry for make.fun's
news-image-20261124 bounty: *Sum up 24 November's world news in one image.*

`entry.png` is a one-page broadsheet front page that sums up the world news of
**Tuesday 24 November 2026**:

- **Lead story** — Ukraine says its sea drones sank a Russian warship off Libya:
  seven unmanned boats struck the corvette *Merkury* near Benghazi, destroying a
  Ka-27 helicopter and hitting the cargo ship MV *Angara*. The panel is drawn in
  code: the warship at dusk, the helicopter above it, seven drone boats with wakes
  closing in, and the strike bursting at its bow.
- **Also on the page** — Russian strikes kill at least 12 in the Kyiv region;
  NATO vows space defence after reports Russia plans a nuclear satellite launch
  within weeks; Nvidia reinstates Jensen Huang as CEO, 11 days after he stepped
  down, after Trump's push; GTA VI hacker Arion Kurtaj, 21, gets seven years in a
  London court; the UN chief calls for a global AI risk-management framework
  within a year; Trump offers the Philippines $2.4 billion for self-defence; and
  a ticker line notes thousands evacuated from a UK concert after an unknown
  substance was released.

## How the image was made

`make_image.py` draws the whole page with Python PIL — masthead, red date band,
lead panel, six story blocks with hand-drawn icons (missile, satellite, chip,
gamepad, globe, shield) and a footer ticker. No photographs and no image
generation: every pixel is vector-style drawing code on a broadsheet palette
(off-white paper, near-black ink, one red accent), set in Noto Sans. The render
is deterministic and the file is 1024 × 1024, well under the 1 MiB gate.

To rebuild the image itself (needs Python 3 with Pillow and the Noto Sans
fonts):

```sh
python3 make_image.py   # rewrites ./entry.png
```

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

The competition program is `main.ts` (Node 22, standard library only). It copies
the shipped `entry.png` to the output directory — `out/entry.png`,
byte-identical to `./entry.png`.

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=a0x1nnrs&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
