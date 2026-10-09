# Changelog

One entry per version. The version is `VERSION` in `index.html`; it shows in About and in the feedback email's subject.

## 1.6.0 — 9 October 2026
A review to tighten loose ends, as done for Metronome.
- Works offline once opened: a service worker keeps the clock, icons and fonts (network first, saved copy after 3 seconds or with no connection).
- About: the origin is told right. The clock that inspired it is glimpsed during the hour-long run across Paris that leads up to the final duel, not in the final act. The intro no longer promises "big hands" and "nothing else", now that Fine hands and Markings exist. It also mentions offline use and reduce motion.
- Respects Reduce Motion: the liquid's surges and the midnight and dawn churn run at a third of their strength. The blackout and the dawn light still fade in and out, slowly.
- Battery: the clock draws at 30 frames a second while calm (most of the time), full speed only for the midnight build, the dawn rounds, the fades and just after a touch, and 10 a second while white, orange or black covers the screen.
- Keyboard: the closed settings panel is no longer reachable with Tab. The Style heading sits at the right level for screen readers.
- Manifest in the family format: "Liquid Clock by bitScribbles", scope, and Ink for the splash and theme colours. Adds the standard `mobile-web-app-capable` tag.
- Tidy: an unused shader function removed, and comments brought up to date.
- `checks/check.py`: browser checks for the centre tap, the panel, keyboard, persistence, the midnight and dawn timelines, Paris sunrise, reduce motion, offline and accessibility (axe). Tooling lives in `checks/`, so the repo root stays plain files.

## 1.5.1 — 8 October 2026
- New app icon, in the family of the other bitScribbles apps: a purple tile with a white clock face, purple liquid rising in its lower half, and deep-purple hands at 10:10. Purple is Liquid Clock's colour, as amber is Metronome's and teal is Clear Tracker's.
- Full icon set: Home Screen (192, 512), a maskable icon for Android, an Apple touch icon and a favicon. Made by `design/make-icons.py` from `design/liquid-icon.svg`.

## 1.5.0 — 8 October 2026
- Midnight: after its ten-minute build of full-screen swirls, at 12:00 everything cuts to black (hands and liquid hidden), holds for about five seconds, then slowly returns to the calm clock over a minute. The swirling dies away under the black.
- Paris dawn, now about a minute: the white holds for about four seconds, then a long wash of orange morning light fades out slowly, and the calm clock is fully back at about sixty seconds.
- Face markings: the numerals 12, 3, 6 and 9 now sit inside the dotted ring, in Space Grotesk (from the bitScribbles brand), and the ring is complete.

## 1.4.0 — 8 October 2026
Inspired by a frame of the film's clock (our own take, not a copy).
- New preset, Seine: sky-blue water with white patches, red blooms, ochre flecks and maroon depths.
- New Style controls under the palettes, remembered like the colours:
  - Edges: Soft (as before) or Ink, a thin dark line along every colour edge, like marbled paper. Each palette has an ink colour; Seine's is maroon.
  - Hands: Bold (as before) or Fine, thin and dark.
  - Face: Plain (as before) or Markings, a dotted minute ring with 12, 3, 6 and 9.
- If a browser can't draw the ink lines, the clock simply stays soft.

## 1.3.2 — 7 October 2026
- Dawn blast: the screen burns warm white (hands and swirls hidden), gives way to orange morning light at about two seconds, and returns to the regular clock by ten seconds. The blast's churn now dies away while the screen is still white, so the fade reveals the calm clock, not full-screen swirls.

## 1.3.1 — 7 October 2026
- The dawn blast is a full whiteout: warm white covers the whole screen, hands included, within half a second of sunrise, holds for a second, then fades back to the flowing clock over about ten seconds.

## 1.3.0 — 7 October 2026
- New preset, Ballerina: rose and blush veins on snow white, with fire orange as the accent, hot pink at the hand tips, deep rose hands, and spatters of ice blue, gold and flame.
- Dawn in Paris, wherever you are: at sunrise in Paris (worked out for each day, shown in About in your local time), the liquid builds three times, at five, three and one minute before, each round cut short, then breaks in a flash of warm light at the moment of sunrise and settles over the next minute or so.
- Fix: at the height of the midnight flood the liquid broke into a blocky grid. The ripple warp now stays near the hands, and big events churn through the noise itself, so the whole screen moves like liquid.
- `?dawn` in the address previews the run-up to the next Paris dawn.

## 1.2.1 — 7 October 2026
- About: the disclaimer now signs off with "The hour is always closer than you think. Tick tock."

## 1.2.0 — 7 October 2026
- The settings panel now wears the bitScribbles brand, dark only: the ink-to-purple gradient, Teal for the selected tab, selected palette, Done and Send feedback, Purple for section labels and the secondary button.
- Brand type: Space Grotesk for the title, Inter for text, JetBrains Mono for labels and the version, and the "by <bit/>Scribbles" byline in Caveat, as in Metronome. The fonts are served from the app's own `fonts/` folder (about 150 KB, SIL Open Font License), so nothing loads from elsewhere.
- The clock face keeps its film look; only the first-visit hint on the clock stays in the serif.

## 1.1.0 — 6 October 2026
- Settings open with a touch at the centre of the clock. The gold coin button is gone; nothing else on screen is a button. A touch at the centre also stirs the liquid.
- First visit only: a faint "Touch the centre" hint along the bottom edge, then never again.
- New About page beside Colours: how the clock moves, keeping it on display (iPhone and Android), made by bitScribbles, privacy, disclaimer, support (feedback email, Buy me a coffee) and credits.
- Screen wake lock asked for on the first touch with pointer events (Safari on iPhone doesn't send clicks on the canvas), and asked again when the page comes back into view.
- Escape closes the panel; the centre target can be reached with the keyboard.
- LICENSE copyright now reads "Hugh Lindsay (Huge Enterprises)", matching the other bitScribbles apps.

## 1.0.0 — 5 October 2026
- Liquid analog clock: churn around the hands, the minute surge, the midnight flood.
- Six colour presets (Marquis, Sacré-Cœur, High Table, Osaka Neon, Continental, Berlin) and a custom palette, remembered in the browser.
- Installable from the Home Screen (manifest and icons). `?t=23:58` previews a time.
