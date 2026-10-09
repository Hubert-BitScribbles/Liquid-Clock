"""Browser checks for Liquid Clock: behaviour, timed events, accessibility (axe), offline.

Run from the repo root after `cd checks && npm install`:
    python3 checks/check.py
Needs Python Playwright with Chromium. Screenshots go to checks/out/.
"""
import http.server, os, socketserver, threading, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "checks", "out"); os.makedirs(S, exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=ROOT)); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://localhost:{PORT}/"
axe = open(os.path.join(ROOT, "checks", "node_modules", "axe-core", "axe.min.js")).read()
INIT = "window.__wake=0;Object.defineProperty(navigator,'wakeLock',{value:{request:async()=>{window.__wake++;return new EventTarget();}}});"
fails = []
def ok(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)
def audit(pg, tag):
    pg.evaluate(axe)
    r = pg.evaluate("axe.run(document.getElementById('pn'),{runOnly:['wcag2a','wcag2aa','wcag21aa','wcag22aa','best-practice']}).then(r=>r.violations.map(v=>v.id+' ('+v.nodes.length+'): '+v.nodes.slice(0,3).map(n=>n.target.join(' ')).join(' | ')))")
    ok(not r, f'{tag} axe: {r or "none"}')
def at(pg, base_js, x):           # move the clock to x seconds from an event and let it settle
    pg.evaluate(f"x=>{{window.__B={base_js};off=window.__B+x-Date.now()}}", int(x*1000)); pg.wait_for_timeout(500)
    pg.evaluate("x=>{off=window.__B+x-Date.now()}", int(x*1000)); pg.wait_for_timeout(50)
    return pg.evaluate("state()")

with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
    ctx = b.new_context(viewport={"width": 844, "height": 390}, device_scale_factor=2, has_touch=True, is_mobile=True)
    ctx.add_init_script(INIT)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(1500)
    ok(pg.evaluate("gl.getProgramParameter(pr,gl.LINK_STATUS)"), 'shader compiles and links')
    ok(pg.evaluate("document.fonts.check('500 20px \"Space Grotesk\"')"), 'Space Grotesk loaded for the face numerals')
    pg.screenshot(path=S + "/clock.png")

    # the settings panel: only the centre opens it; closed, it can't be reached by keyboard
    open_ = lambda: pg.evaluate("document.getElementById('pn').classList.contains('open')")
    pg.touchscreen.tap(780, 40); pg.wait_for_timeout(300); ok(not open_(), 'a tap away from the centre does nothing')
    ok(pg.evaluate("window.__wake") >= 1, 'the first touch asks for the screen to stay on')
    pg.keyboard.press('Tab'); pg.keyboard.press('Tab')
    ok(pg.evaluate("!document.getElementById('pn').contains(document.activeElement)"), 'closed panel is out of the keyboard order')
    pg.touchscreen.tap(422, 195); pg.wait_for_timeout(600); ok(open_(), 'a tap at the centre opens the panel')
    audit(pg, 'Colours')
    pg.click('.pc[data-id=custom]'); pg.wait_for_timeout(300); audit(pg, 'Custom colours')
    pg.click('#tAbout'); pg.wait_for_timeout(300); audit(pg, 'About')
    ok('final duel' in pg.inner_text('#vAbout') and 'final act' not in pg.inner_text('#vAbout'), 'About tells the origin right')
    ok(pg.inner_text('#ver') == pg.evaluate("VERSION"), 'About shows the version')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(500); ok(not open_(), 'Escape closes the panel')

    # style choices persist
    pg.evaluate("palId='seine';applyPalette();STYLE.ink='1';STYLE.hands='fine';STYLE.face='marks';applyStyle()")
    pg.reload(); pg.wait_for_timeout(1200)
    ok(pg.evaluate("palId==='seine'&&STYLE.ink==='1'&&STYLE.hands==='fine'&&STYLE.face==='marks'"), 'palette and style survive a reload')
    pg.screenshot(path=S + "/seine-styled.png")

    # midnight: black within a moment, calm under it, clear after a minute
    M = "(()=>{const d=new Date();d.setHours(24,0,0,0);return d.getTime()})()"
    s = at(pg, M, -60); ok(s['mid'] > .7 and s['black'] == 0, 'midnight: swirls build before 12:00')
    s = at(pg, M, 3);   ok(s['black'] > .99, 'midnight: black at 12:00')
    s = at(pg, M, 5);   ok(s['mid'] < .05, 'midnight: churn gone under the black')
    s = at(pg, M, 65);  ok(s['black'] == 0, 'midnight: clock back after a minute')
    # Paris dawn: three rounds, white, orange, calm
    D = "dawnNext(Date.now())"
    for c in (-300, -180, -60):
        s = at(pg, D, c - 2); ok(s['mid'] > .4, f'dawn: round at {c} s builds')
    s = at(pg, D, 2);  ok(s['white'] > .99 and s['sun'] > .99, 'dawn: white over orange at sunrise')
    s = at(pg, D, 20); ok(s['white'] == 0 and s['sun'] > .3 and s['mid'] < .05, 'dawn: orange light, calm beneath')
    s = at(pg, D, 65); ok(s['sun'] == 0, 'dawn: clock back after a minute')
    ok(pg.evaluate("Math.abs(parisSunrise(Date.UTC(2026,5,21))-Date.UTC(2026,5,21,3,47))") < 180e3, 'Paris sunrise on 21 June 2026 within 3 minutes of 05:47 CEST')

    # reduce motion: a calmer clock
    rm = b.new_context(viewport={"width": 844, "height": 390}, reduced_motion='reduce').new_page()
    rm.goto(URL + "?t=23:59:00"); rm.wait_for_timeout(800)
    ok(rm.evaluate("state().mid") < .4, 'reduce motion: midnight build is gentler')

    # offline: the service worker serves the clock with no connection
    pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_timeout(1000)
    ctx.set_offline(True); pg.reload(); pg.wait_for_timeout(1500)
    ok(pg.evaluate("typeof VERSION!=='undefined' && document.fonts.check('500 20px \"Space Grotesk\"')"), 'opens offline, fonts included')
    ctx.set_offline(False)

    ok(not errs, f'no page errors {errs or ""}')
    b.close()
print('\n' + ('All checks passed.' if not fails else f'{len(fails)} failed.'))
