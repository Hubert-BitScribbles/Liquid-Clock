# Liquid Clock

A liquid analog clock by bitScribbles: two big hands over a living background, with a surge every minute and a flood at midnight.

Live at https://liquidclock.bitscribbles.com

## How it's built
One self-contained `index.html` — WebGL for the liquid, a 2D canvas for the hands, no libraries or build step — plus `manifest.json` and the two icons for installing to the Home Screen, and the brand fonts used by the settings panel in `fonts/` (SIL Open Font License, see `fonts/OFL.txt`).

## Working on it
- Changes go on a branch; merge to `main` to publish (Cloudflare deploys `main`).
- Bump `VERSION` in `index.html` on the branch, with an entry in `CHANGELOG.md`. The last number is for fixes, the middle one for features.
- Add `?t=23:58` to the address to preview a time (useful for the midnight flood).

## Licence
MIT — see `LICENSE`.
