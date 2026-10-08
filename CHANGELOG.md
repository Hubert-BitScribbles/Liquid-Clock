# Changelog

One entry per version. The version is `VERSION` in `index.html`; it shows in About and in the feedback email's subject.

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
