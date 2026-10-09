# Icon E "The half-full face": purple tile, Paper clock face, purple liquid rising in it, deep-purple hands at 10:10.
# Drawn on 100x100 in the bitScribbles palette (Purple #6E56CF, Paper #FAFAF9).
# Run from the repo root: python3 design/make-icons.py (needs Playwright).
from playwright.sync_api import sync_playwright
PAPER='#FAFAF9';PURPLE='#6E56CF';DEEP='#4B3A9A'
def svg(scale=1.0, rounded=False):
    k=scale; t=lambda v:50+(v-50)*k          # scale the mark about the centre
    tile=f'<rect width="100" height="100" rx="22.5" fill="{PURPLE}"/>' if rounded else f'<rect width="100" height="100" fill="{PURPLE}"/>'
    wave=(f'M{t(16)} {t(57)} C{t(28)} {t(47)} {t(38)} {t(68)} {t(51)} {t(58)} S{t(72)} {t(46)} {t(86)} {t(59)} '
          f'L{t(86)} {t(90)} L{t(16)} {t(90)}Z')
    h1,h2=4.6*k,3.4*k
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{tile}'
      f'<defs><clipPath id="c"><circle cx="50" cy="50" r="{30*k}"/></clipPath></defs>'
      f'<circle cx="50" cy="50" r="{30*k}" fill="{PAPER}"/>'
      f'<g clip-path="url(#c)"><path d="{wave}" fill="{PURPLE}" opacity=".9"/></g>'
      f'<line x1="50" y1="50" x2="{t(38.5)}" y2="{t(43.4)}" stroke="{DEEP}" stroke-width="{h1}" stroke-linecap="round"/>'
      f'<line x1="50" y1="50" x2="{t(68)}" y2="{t(39.6)}" stroke="{DEEP}" stroke-width="{h2}" stroke-linecap="round"/>'
      f'<circle cx="50" cy="50" r="{h1*.8}" fill="{DEEP}"/></svg>')
out = {  # path: (size, scale, rounded)
 'icon-512.png':(512,1,True), 'icon-192.png':(192,1,True),
 'maskable-512.png':(512,.8,False), 'apple-touch-icon.png':(180,1,False), 'favicon.png':(64,1,True)}
with sync_playwright() as p:
    b=p.chromium.launch()
    for path,(n,s,r) in out.items():
        pg=b.new_page(viewport={'width':n,'height':n})
        pg.set_content(f'<html><body style="margin:0;background:transparent">{svg(s,r).replace("<svg ","<svg width=%d height=%d "%(n,n))}</body></html>')
        pg.screenshot(path=path, omit_background=r, clip={'x':0,'y':0,'width':n,'height':n}); pg.close()
    b.close()
open('design/liquid-icon.svg','w').write(svg(1,True))
