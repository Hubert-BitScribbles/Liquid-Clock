# Changelog

One entry per version. The version is `VERSION` in `index.html`; it shows in About and in the feedback email's subject.

## 1.3.0 — 7 October 2026
- New preset, Ballerina: rose and blush veins on snow white, with fire orange as the accent, hot pink at the hand tips, deep rose hands, and spatters of ice blue, gold and flame.

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
