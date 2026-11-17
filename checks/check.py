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
SEEN = "try{localStorage.setItem('lc.welcomed','1')}catch(e){}"   # past the welcome, for checks about the clock itself
SAFARI27 = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/27.2 Mobile/15E148 Safari/604.1'
SAFARI26 = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Mobile/15E148 Safari/604.1'
fails = []
def ok(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)
def audit(pg, tag, el='pn'):
    pg.evaluate(axe)
    r = pg.evaluate("axe.run(document.getElementById('"+el+"'),{runOnly:['wcag2a','wcag2aa','wcag21aa','wcag22aa','best-practice']}).then(r=>r.violations.map(v=>v.id+' ('+v.nodes.length+'): '+v.nodes.slice(0,3).map(n=>n.target.join(' ')).join(' | ')))")
    ok(not r, f'{tag} axe: {r or "none"}')
def now_at(pg, base_js, x):       # set the time and read the state in one step (bursts make frames slow here)
    return pg.evaluate(f"x=>{{off=({base_js})+x-Date.now();return state()}}", int(x*1000))
def at(pg, base_js, x):           # move the clock to x seconds from an event and let it settle
    pg.evaluate(f"x=>{{window.__B={base_js};off=window.__B+x-Date.now()}}", int(x*1000)); pg.wait_for_timeout(500)
    pg.evaluate("x=>{off=window.__B+x-Date.now()}", int(x*1000)); pg.wait_for_timeout(50)
    return pg.evaluate("state()")

with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
    ctx = b.new_context(viewport={"width": 844, "height": 390}, device_scale_factor=2, has_touch=True, is_mobile=True)
    ctx.add_init_script(INIT); ctx.add_init_script(SEEN)
    def page(**kw):
        c = b.new_context(**kw); c.add_init_script(SEEN); return c.new_page()
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
    # the phone standard (brand guide, 12 November 2026): 44px targets, text that grows, nothing sideways
    small = pg.evaluate("""[...document.querySelectorAll('#pn button,#pn select,#pn .links a,#cu label')].filter(e=>e.offsetParent)
       .map(e=>{const r=e.getBoundingClientRect();return [e.id||e.textContent.trim().slice(0,20)||e.dataset.k,Math.round(r.width),Math.round(r.height)]})
       .filter(([n,w,h])=>h<44||(w<44&&!/^#/.test(n)))""")
    ok(not small, f'Settings: every control at least 44px to tap {small or ""}')
    # the selected palette's ring (outline 2px, offset 3px) fits inside the scrolling body, in every column
    clip = pg.evaluate("""(()=>{const b=document.getElementById('pbody').getBoundingClientRect(),out=[];
      for(const id of Object.keys(PRESETS)){palId=id;applyPalette();const r=document.querySelector('.pc.on i').getBoundingClientRect();
        if(r.left-5<b.left-.5||r.right+5>b.right+.5)out.push(id)}palId='marquis';applyPalette();return out})()""")
    ok(not clip, f'Settings: the selected ring is never clipped {clip or ""}')
    ok(pg.evaluate("[...document.querySelectorAll('#st h3')].map(h=>h.textContent).join()") == 'Clock,Liquid,Moments' and pg.text_content('#tCol') == 'Settings',
       'Settings: grouped as Colours, Clock, Liquid, Moments')
    pg.click('#tAbout'); pg.wait_for_timeout(300); audit(pg, 'About')
    ok('final duel' in pg.inner_text('#vAbout') and 'final act' not in pg.inner_text('#vAbout'), 'About tells the origin right')
    ok(pg.inner_text('#ver') == pg.evaluate("VERSION"), 'About shows the version')
    ok(pg.evaluate("[...document.querySelectorAll('#vAbout a')].some(a=>a.href==='https://bitscribbles.com/takepart.html'&&a.textContent==='Contribute')")
       and 'coffee' not in pg.inner_text('#vAbout').lower() and '™' not in pg.inner_text('#vAbout'), 'About links Contribute to Take part, no coffee link')
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
    a = pg.evaluate("tiltAt=-1e9;mouseAt=-1e9;for(let i=0;i<20;i++)tiltStep(.1);tilt.slice()"); pg.wait_for_timeout(4000)   # the drift is slow, and can sit at a turning point
    ok(pg.evaluate("t=>{for(let i=0;i<20;i++)tiltStep(.1);return Math.hypot(tilt[0]-t[0],tilt[1]-t[1])}", a) > .05, 'depth: with no tilt sensor it drifts on its own')
    pg.screenshot(path=S + "/seine-deep.png")
    pg.evaluate("STYLE.depth='off';applyStyle()"); pg.wait_for_timeout(200)
    ok(pg.evaluate("gl.getUniform(pr,uPara)===0&&gl.getUniform(pr,uLit)===0"), 'depth: Off turns the shader effects off')
    dm = page(viewport={"width": 1280, "height": 800})
    dm.goto(URL); dm.wait_for_timeout(600); dm.evaluate("STYLE.depth='para';applyStyle()")
    dm.mouse.move(1270, 10); dm.wait_for_timeout(300)
    ok(dm.evaluate("for(let i=0;i<20;i++)tiltStep(.1);tilt[0]>.8&&tilt[1]>.8"), 'depth: on a computer the mouse stands in for tilt')
    dm.context.close()

    # midnight: black within a moment, calm under it, clear after a minute
    M = "(()=>{const d=new Date();d.setHours(24,0,0,0);return d.getTime()})()"
    s = at(pg, M, -60); ok(s['mid'] > .7 and s['black'] == 0, 'midnight: swirls build before 12:00')
    s = at(pg, M, 3);   ok(s['black'] > .99, 'midnight: black at 12:00')
    s = at(pg, M, 5)    # midnight's own churn: in late November, Paris dawn falls just after midnight in Vancouver
    ok(s['mid'] - pg.evaluate("dawnState(Date.now()+off).ev*(CALM.matches?.3:1)") < .05, 'midnight: churn gone under the black')
    s = at(pg, M, 65);  ok(s['black'] == 0, 'midnight: clock back after a minute')
    # Paris dawn: three rounds, white, orange, calm
    D = "dawnNext(Date.now())"
    for c in (-300, -180, -60):
        s = at(pg, D, c - 2); ok(s['mid'] > .4, f'dawn: round at {c} s builds')
    s = at(pg, D, 2);  ok(s['white'] > .99 and s['sun'] > .99, 'dawn: white over orange at sunrise')
    s = at(pg, D, 20)    # dawn's own churn: in some time zones Paris dawn falls in the run-up to local midnight (11:51 pm in Vancouver in November)
    ok(s['white'] == 0 and s['sun'] > .3 and pg.evaluate("dawnState(dawnNext(Date.now()-60e3)+20e3).ev") < .05, 'dawn: orange light, calm beneath')
    s = at(pg, D, 65); ok(s['sun'] == 0, 'dawn: clock back after a minute')
    # bursts: one every hour; ink coming faster into midnight and flooding to black; light at dawn; colour at New Year
    Hr = "(()=>{const d=new Date();d.setHours(d.getHours()+1,0,0,0);if(d.getHours()===0)d.setHours(1);return d.getTime()})()"
    s = now_at(pg, Hr, 2); ok(len(s['bs']) == 1 and s['bs'][0]['a'] > .9 and s['busy'], 'hours: one burst at the top of the hour, drawn at full speed')
    s = now_at(pg, Hr, 14); ok(len(s['bs']) == 0, 'hours: gone within fourteen seconds')
    sz = lambda hh: now_at(pg, f"new Date(2026,10,20,{hh},0,0).getTime()", 7)['bs'][0]
    a1, a23, b23 = sz(1), sz(23), now_at(pg, "new Date(2026,10,21,23,0,0).getTime()", 7)['bs'][0]
    ok(a1['r'] < .1 and .25 < a23['r'] < .35, 'hours: small at 1 am, growing every hour, but never more than about a third of the screen')
    s = now_at(pg, Hr, 1); t = now_at(pg, Hr, 7)
    ok(len(s['bs']) == 1 and s['bs'][0]['pop'] == 0 and len(t['bs']) == 1 and t['bs'][0]['pop'] == 1 and s['bs'][0]['r'] < t['bs'][0]['r'] / 2,
       'hours: the drop swells slowly first (3-5 s), then bursts')
    ok(abs(a23['x'] - b23['x']) + abs(a23['y'] - b23['y']) > .05, 'hours: lands somewhere different from day to day')
    pg.evaluate("STYLE.hours='off'"); s = now_at(pg, Hr, 2); pg.evaluate("STYLE.hours='on'")
    ok(len(s['bs']) == 0, 'hours: Off means no burst')
    s = now_at(pg, M, -20); ok(len(s['bs']) >= 1, 'midnight: ink bursts through the last minute')
    def groups(base, x0, x1):   # across a stretch of time (one step, in the page): any drop on its own, any two of different shades overlapping
        return pg.evaluate(f"""([x0,x1])=>{{const B={base};let alone=false,pair=false;
          for(let x=x0;x<x1;x+=.5){{off=B+x*1000-Date.now();const v=state().bs.filter(b=>b.pop===1&&b.a>.5);
            for(const p of v){{const o=v.filter(q=>q!==p&&Math.hypot(p.x-q.x,p.y-q.y)<p.r+q.r);
              alone=alone||!o.length;pair=pair||o.some(q=>q.col.join()!==p.col.join())}}}}return[alone,pair]}}""", [x0, x1])
    ok(all(groups(M, -59, -1)), 'midnight: ink lands alone or in overlapping shades')
    s = now_at(pg, M, -.5); ok(sum(b['pop'] == 0 for b in s['bs']) >= 4, 'midnight: the great drops swell before 12:00')
    s = now_at(pg, M, 1); ok(len(s['bs']) >= 6 and 0 < s['black'] < 1, 'midnight: the ink floods in as the black arrives')
    s = now_at(pg, D, -298); ok(len(s['bs']) >= 3 and all(b['col'][0] > .9 for b in s['bs']), 'dawn: a volley of light with the first round')
    s = now_at(pg, D, .2); ok(any(b['r'] > 1 for b in s['bs']) and s['white'] == 0, 'dawn: one great burst of light, before the white')
    NY = "new Date(new Date().getFullYear()+1,0,1).getTime()"
    s = now_at(pg, NY, -4); ok(len(s['bs']) >= 3 and s['blk'] == 0, 'New Year: the last seconds count down in ink')
    ok(all(groups(NY, 7, 40)), 'New Year: colour lands alone or in overlapping shades')
    s = now_at(pg, NY, 15); ok(s['blk'] == 1 and s['hide'] == 1 and s['black'] == 0 and len(s['bs']) >= 3, 'New Year: colour breaks through the black')
    s = now_at(pg, NY, 600); ok(len(s['bs']) == 3 and all(b['a'] < .2 for b in s['bs']) and s['blk'] == 0, 'New Year: faint stains linger into the first hour')
    s = now_at(pg, NY, 3700); ok(len(s['bs']) == 0, 'New Year: the stains are gone after an hour')
    s = now_at(pg, M, 3); ok(s['blk'] == 0 and s['black'] == 1, 'an ordinary midnight stays black')
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
    ls = page(viewport={"width": 844, "height": 350}, has_touch=True, is_mobile=True)
    ls.goto(URL); ls.wait_for_timeout(800); ls.touchscreen.tap(422, 175); ls.wait_for_timeout(600)
    ls.evaluate("document.querySelector('.pc[data-id=custom]').scrollIntoView({block:'center'})"); ls.wait_for_timeout(200)
    bb = ls.query_selector('.pc[data-id=custom]').bounding_box(); ls.touchscreen.tap(bb['x']+bb['width']/2, bb['y']+bb['height']/2); ls.wait_for_timeout(400)
    ls.evaluate("document.getElementById('pbody').scrollTop=9999"); ls.wait_for_timeout(200)
    d = ls.evaluate("(()=>{const r=document.getElementById('pd').getBoundingClientRect();return [r.top,r.bottom,innerHeight]})()")
    ok(d[0] >= 0 and d[1] <= d[2], f'panel: Done stays on screen sideways after scrolling to Custom (top {d[0]:.0f})')

    # reduce motion: a calmer clock
    rm = page(viewport={"width": 844, "height": 390}, reduced_motion='reduce')
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
    pg.evaluate("fetch('clips/install-iphone-safari.jpg').then(r=>r.blob())"); pg.wait_for_timeout(400)
    ok(pg.evaluate("caches.keys().then(ks=>Promise.all(ks.map(k=>caches.open(k).then(c=>c.keys())))).then(a=>a.flat().every(r=>!r.url.includes('/clips/')))"),
       'the install clips are never kept offline')

    # larger text: at twice the usual size (as iPhone's largest standard Larger Text setting), nothing runs sideways
    for w_, h_ in [(390, 844), (320, 568)]:
        lt = page(viewport={"width": w_, "height": h_}, is_mobile=True, has_touch=True)
        lt.goto(URL); lt.wait_for_timeout(800); lt.evaluate("document.documentElement.style.setProperty('--t','2px');palId='custom';custom={...PRESETS.marquis,name:'Custom'};applyPalette();openPanel()"); lt.wait_for_timeout(500)
        wide = lt.evaluate("""[...document.querySelectorAll('#pn *')].filter(e=>e.offsetParent&&e.getBoundingClientRect().right>innerWidth+1).map(e=>e.id||e.className||e.tagName).slice(0,5)""")
        lt.click('#tAbout'); lt.wait_for_timeout(200)
        wide += lt.evaluate("""[...document.querySelectorAll('#vAbout *')].filter(e=>e.offsetParent&&e.getBoundingClientRect().right>innerWidth+1).map(e=>e.id||e.className||e.tagName).slice(0,5)""")
        ok(not wide, f'larger text (200%) at {w_}px: nothing runs off the side {wide or ""}')
        lt.context.close()

    # welcome: first visit only; what it is and where the settings are; then install steps for the device
    def iphone(ua=SAFARI27, init=None, **kw):
        c = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=True, is_mobile=True, user_agent=ua, **kw)
        if init: c.add_init_script(init)
        w = c.new_page(); w.on("pageerror", lambda e: errs.append(str(e))); w.goto(URL); w.wait_for_timeout(1400); return w
    shown = lambda w: w.evaluate("document.getElementById('ob').classList.contains('open')")
    w = iphone()
    ok(shown(w) and w.is_visible('#ob1') and not w.is_visible('#ob2'), 'welcome: opens on the first visit, at screen 1')
    ok(w.evaluate("document.activeElement.id") == 'obT1' and 'Touch the centre' in w.inner_text('#ob1'), 'welcome: focus on its title; says to touch the centre for settings')
    w.screenshot(path=S + "/welcome-1.png"); audit(w, 'Welcome 1', 'ob')
    w.click('#obNext'); w.wait_for_timeout(300)
    steps = w.inner_text('#obSteps')
    ok(w.is_visible('#ob2') and '≡' in steps and 'View More' in steps and 'Open as Web App' in steps and 'an iPhone, in Safari' in w.inner_text('#obDev'),
       'welcome: Safari 27 on iPhone gets ≡ → Share → View More → Add')
    ok(w.is_visible('#obPlay') and '26 s' in w.inner_text('#obPlay') and not w.is_visible('#obVid'), 'welcome: Safari clip offered, closed until tapped')
    w.click('#obPlay'); w.wait_for_timeout(1200)
    ok(w.evaluate("obVid.src.startsWith('blob:')&&obVid.muted&&obVid.loop&&obVid.playsInline&&obVid.getAttribute('aria-label').includes('Add to Home Screen')"),
       'welcome: the clip plays muted, looping, inline, from memory, with the steps as its label')
    w.screenshot(path=S + "/welcome-2.png"); audit(w, 'Welcome 2 with clip', 'ob')
    w.click('#obChange'); w.select_option('#obOs', 'android'); w.select_option('#obBr', 'chrome'); w.wait_for_timeout(200)
    ok('Install app' in w.inner_text('#obSteps') and not w.is_visible('#obClip') and w.evaluate("JSON.parse(localStorage.getItem('lc.device')).os") == 'android',
       'welcome: Not right? Change switches the steps, hides the clip, and is remembered')
    w.select_option('#obOs', 'iphone'); w.select_option('#obBr', 'safari'); w.wait_for_timeout(200)
    ok(w.evaluate("localStorage.getItem('lc.device')") is None, 'welcome: choosing the detected device again goes back to detecting')
    w.click('#obDone'); w.wait_for_timeout(300)
    ok(not shown(w) and w.evaluate("localStorage.getItem('lc.welcomed')") == '1' and w.evaluate("document.activeElement.id") == 'hub',
       'welcome: Start the clock closes it, remembers, and leaves focus on the centre')
    w.reload(); w.wait_for_timeout(1400); ok(not shown(w), 'welcome: not shown again')
    w.click('#hub', force=True); w.wait_for_timeout(500); w.click('#tAbout'); w.wait_for_timeout(200); w.click('#howTo'); w.wait_for_timeout(400)
    ok(shown(w) and w.is_visible('#ob2') and not w.evaluate("document.getElementById('pn').classList.contains('open')"), 'welcome: About → How to install opens the install screen')
    w.keyboard.press('Escape'); w.wait_for_timeout(200); ok(not shown(w), 'welcome: Escape closes it')
    w.context.close()
    w = iphone(SAFARI26); w.click('#obNext'); w.wait_for_timeout(200)
    ok('⋯' in w.inner_text('#obSteps') and not w.is_visible('#obClip'), 'welcome: Safari 26 gets ⋯ and no clip')
    w.context.close()
    w = iphone(init="localStorage.setItem('lc.hinted','1')")
    ok(not shown(w), 'welcome: not shown to people who were already here')
    w.context.close()
    w = iphone(init="Object.defineProperty(navigator,'standalone',{value:true})")
    ok(shown(w) and w.inner_text('#obNext') == 'Start the clock' and not w.is_visible('#howWrap'), 'welcome: installed, just screen 1, and no How to install')
    w.click('#obNext'); w.wait_for_timeout(200); ok(not shown(w), 'welcome: installed, Start the clock closes it')
    w.context.close()

    ok(not errs, f'no page errors {errs or ""}')
    b.close()
print('\n' + ('All checks passed.' if not fails else f'{len(fails)} failed.'))
