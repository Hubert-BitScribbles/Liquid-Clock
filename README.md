# Liquid Clock

A liquid analog clock by bitScribbles: two hands over a living background, with a surge every minute, a blackout at midnight and a burst of light at dawn in Paris.

Live at https://liquidclock.bitscribbles.com

## How it's built
Plain files, no build step, served as they are from `main` by a Cloudflare Worker:
- `index.html` — everything: WebGL for the liquid, a 2D canvas for the hands and face, the settings panel and About.
- `sw.js` — the service worker that lets the clock open offline. Bump `CACHE` with each release.
- `manifest.json` and the icons (`icon-192.png`, `icon-512.png`, `maskable-512.png`, `apple-touch-icon.png`, `favicon.png`), made by `design/make-icons.py` from `design/liquid-icon.svg`.
- `fonts/` — the brand fonts, self-hosted (SIL Open Font License, see `fonts/OFL.txt`).

## Working on it
- Changes go on a branch and a pull request; merging to `main` publishes.
- Bump `VERSION` in `index.html` **and** `CACHE` in `sw.js` on the branch, with an entry in `CHANGELOG.md`. The last number is for fixes, the middle one for features.
- Checks: `cd checks && npm install` once, then `python3 checks/check.py` from the repo root (needs Python Playwright with Chromium).
- Previews in the address: `?t=23:59:30` to fake a time (midnight), `?dawn` for the run-up to the next Paris dawn.

## Licence
MIT — see `LICENSE`. The fonts are under the SIL Open Font License.
