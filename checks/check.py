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
    ok(pg.evaluate("[...document.querySelectorAll('#vAbout a')].some(a=>a.href==='https://bitscribbles.com/takepart.html'&&a.textContent==='Contribute')")
       and 'coffee' not in pg.inner_text('#vAbout').lower(), 'About links Contribute to Take part, no coffee link')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(500); ok(not open_(), 'Escape closes the panel')

    # style choices persist
    pg.evaluate("palId='seine';applyPalette();STYLE.ink='1';STYLE.hands='fine';STYLE.face='marks';STYLE.secs='on';STYLE.depth='deep';applyStyle()")
    pg.reload(); pg.wait_for_timeout(1200)
    ok(pg.evaluate("palId==='seine'&&STYLE.ink==='1'&&STYLE.hands==='fine'&&STYLE.face==='marks'&&STYLE.secs==='on'&&STYLE.depth==='deep'"), 'palette and style (Seconds and Depth too) survive a reload')
    ok(pg.evaluate("(()=>{off=new Date(2026,0,1,10,8,45).getTime()-Date.now();const s=state();return Math.abs(s.sa-1.5*Math.PI)<.01&&gl.getUniform(pr,uSec)===1})()"), 'Seconds: the second hand points at 9 at 45 s')
    pg.click('#hub', force=True); pg.wait_for_timeout(500)
    ok(pg.evaluate("[...document.querySelectorAll('.seg[data-k=depth] button')].map(b=>b.textContent+':'+b.getAttribute('aria-pressed')).join()") == 'Off:false,Parallax:false,Deep:true' and pg.evaluate("[...document.querySelectorAll('.seg[data-k=secs] button')].map(b=>b.textContent+':'+b.getAttribute('aria-pressed')).join()") == 'Off:false,On:true',
       'Style offers Seconds (Off, On) and Depth (Off, Parallax, Deep)')
    audit(pg, 'Colours with Depth')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
    pg.screenshot(path=S + "/seine-styled.png")

    # depth: tilt moves the hands and the liquid; with no sensor it drifts on its own; Off holds everything still
    # (software rendering here is slow, so step the tilt directly rather than waiting on frames)
    ok(pg.evaluate("tiltAim=[1,-1];tiltAt=performance.now();for(let i=0;i<20;i++)tiltStep(.1);tilt[0]>.9&&tilt[1]<-.9"), 'depth: the picture follows the tilt')
    a = pg.evaluate("tiltAt=-1e9;mouseAt=-1e9;for(let i=0;i<20;i++)tiltStep(.1);tilt.slice()"); pg.wait_for_timeout(1500)
    ok(pg.evaluate("t=>{for(let i=0;i<20;i++)tiltStep(.1);return Math.hypot(tilt[0]-t[0],tilt[1]-t[1])}", a) > .05, 'depth: with no tilt sensor it drifts on its own')
    pg.screenshot(path=S + "/seine-deep.png")
    pg.evaluate("STYLE.depth='off';applyStyle()"); pg.wait_for_timeout(200)
    ok(pg.evaluate("gl.getUniform(pr,uPara)===0&&gl.getUniform(pr,uLit)===0"), 'depth: Off turns the shader effects off')
    dm = b.new_context(viewport={"width": 1280, "height": 800}).new_page()
    dm.goto(URL); dm.wait_for_timeout(600); dm.evaluate("STYLE.depth='para';applyStyle()")
    dm.mouse.move(1270, 10); dm.wait_for_timeout(300)
    ok(dm.evaluate("for(let i=0;i<20;i++)tiltStep(.1);tilt[0]>.8&&tilt[1]>.8"), 'depth: on a computer the mouse stands in for tilt')
    dm.context.close()

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
    s = at(pg, D, 20)    # dawn's own churn: in some time zones Paris dawn falls in the run-up to local midnight (11:51 pm in Vancouver in November)
    ok(s['white'] == 0 and s['sun'] > .3 and pg.evaluate("dawnState(dawnNext(Date.now()-60e3)+20e3).ev") < .05, 'dawn: orange light, calm beneath')
    s = at(pg, D, 65); ok(s['sun'] == 0, 'dawn: clock back after a minute')
    ok(pg.evaluate("Math.abs(parisSunrise(Date.UTC(2026,5,21))-Date.UTC(2026,5,21,3,47))") < 180e3, 'Paris sunrise on 21 June 2026 within 3 minutes of 05:47 CEST')

    # battery: 30 fps while calm, every frame for the big moments, 10 fps under full cover
    gap = lambda base_js, x: pg.evaluate(f"x=>{{const B={base_js};off=B+x-Date.now();return frameGap(state(),1e9)}}", int(x*1000))  # set and read in one go
    calm = gap("Date.now()-(new Date().getSeconds()-25)*1000", 0)
    ok(30 <= calm <= 34, f'battery: calm clock draws at 30 fps (gap {calm:.0f} ms)')
    ok(gap(M, -90) == 0, 'battery: midnight build at full speed')
    ok(gap(M, 3) == 100, 'battery: 10 fps under full black')
    ok(gap(M, 30) == 0, 'battery: full speed while the black fades')
    ok(gap(D, -62) == 0, 'battery: dawn rounds at full speed')
    ok(gap(D, 2) == 100, 'battery: 10 fps under full white')
    ok(pg.evaluate("frameGap({white:0,sun:0,black:0,mid:0},200)") == 0, 'battery: full speed just after a touch')

    # the panel's tabs and Done stay on screen on a short, sideways phone, even after scrolling to Custom
    ls = b.new_context(viewport={"width": 844, "height": 350}, has_touch=True, is_mobile=True).new_page()
    ls.goto(URL); ls.wait_for_timeout(800); ls.touchscreen.tap(422, 175); ls.wait_for_timeout(600)
    ls.evaluate("document.querySelector('.pc[data-id=custom]').scrollIntoView({block:'center'})"); ls.wait_for_timeout(200)
    bb = ls.query_selector('.pc[data-id=custom]').bounding_box(); ls.touchscreen.tap(bb['x']+bb['width']/2, bb['y']+bb['height']/2); ls.wait_for_timeout(400)
    ls.evaluate("document.getElementById('pbody').scrollTop=9999"); ls.wait_for_timeout(200)
    d = ls.evaluate("(()=>{const r=document.getElementById('pd').getBoundingClientRect();return [r.top,r.bottom,innerHeight]})()")
    ok(d[0] >= 0 and d[1] <= d[2], f'panel: Done stays on screen sideways after scrolling to Custom (top {d[0]:.0f})')

    # reduce motion: a calmer clock
    rm = b.new_context(viewport={"width": 844, "height": 390}, reduced_motion='reduce').new_page()
    rm.goto(URL + "?t=23:59:00"); rm.wait_for_timeout(800)
    ok(rm.evaluate("state().mid") < .4, 'reduce motion: midnight build is gentler')
    rm.evaluate("STYLE.depth='deep';applyStyle();tiltAim=[1,1];tiltAt=performance.now();for(let i=0;i<20;i++)tiltStep(.1)")
    ok(rm.evaluate("Math.hypot(tilt[0],tilt[1])<.01") and 'reduce motion' in rm.text_content('#dnote'), 'reduce motion: Depth holds still, and says why')
    rm.context.close()

    # offline: the service worker serves the clock with no connection
    pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_timeout(1000)
    ctx.set_offline(True); pg.reload(); pg.wait_for_timeout(1500)
    ok(pg.evaluate("typeof VERSION!=='undefined' && document.fonts.check('500 20px \"Space Grotesk\"')"), 'opens offline, fonts included')
    ctx.set_offline(False)

    ok(not errs, f'no page errors {errs or ""}')
    b.close()
print('\n' + ('All checks passed.' if not fails else f'{len(fails)} failed.'))
