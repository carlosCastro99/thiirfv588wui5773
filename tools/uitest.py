#!/usr/bin/env python3
"""Smoke-test the app UI: languages, paywall preview, lock states, CJK diagrams.
usage: uitest.py [outdir]"""
import threading, http.server, socketserver, functools, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deeptool import SITE
from playwright.sync_api import sync_playwright
out = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=SITE))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
errs = []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, locale="pt-PT", timezone_id="Europe/Lisbon")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(base + "?store=preview"); pg.wait_for_timeout(600)
    print("lang", pg.evaluate("LANG"), "region", pg.evaluate("S.region"), "gating", pg.evaluate("GATING"))
    pg.screenshot(path=f"{out}/1_home_pt.png")
    pg.evaluate("async()=>{await doDownload(['history','maths','english'])}"); pg.wait_for_timeout(500)
    print("lessons", pg.evaluate("Object.keys(LESSONS).length"))
    pg.evaluate("go({tab:'learn',pack:'history'})"); pg.wait_for_timeout(300); pg.screenshot(path=f"{out}/2_pack_locked.png")
    pg.evaluate("openPaywall('history')"); pg.wait_for_timeout(300); pg.screenshot(path=f"{out}/3_paywall.png")
    pg.click("[data-pwbuy]"); pg.wait_for_timeout(300)
    print("ent", pg.evaluate("JSON.stringify(S.ent)"))
    pg.evaluate("go({tab:'feed'})"); pg.wait_for_timeout(500); pg.screenshot(path=f"{out}/4_feed.png")
    pg.evaluate("go({tab:'you'})"); pg.wait_for_timeout(300); pg.screenshot(path=f"{out}/5_you.png", full_page=True)
    for lang in ["en", "es", "fr", "zh", "pt-BR"]:
        pg.evaluate(f"setLang('{lang}')"); pg.wait_for_timeout(400)
        vis = pg.evaluate("Object.values(LESSONS).some(l=>l.pack==='english')")
        print(lang, "english topic visible:", vis)
        pg.evaluate("go({tab:'learn'})"); pg.wait_for_timeout(200); pg.screenshot(path=f"{out}/6_learn_{lang}.png")
    pg.evaluate("setLang('zh')"); pg.wait_for_timeout(200)
    svg = pg.evaluate("""()=>{const h=document.createElement('div');h.className='sk paper';h.style.cssText='position:fixed;left:0;top:0;width:340px;z-index:9999;background:#fff';h.innerHTML=VZ({k:'flow',steps:['氢原子核相互碰撞','聚变成氦','质量以能量形式损失','光和热']})+VZ({k:'pairs',items:[{a:'精确率',b:'警报有多可信？'},{a:'召回率',b:'抓到了多少真实案例？'}]});document.body.appendChild(h);return h.innerHTML.length}""")
    pg.wait_for_timeout(400); pg.screenshot(path=f"{out}/7_cjk.png", clip={"x":0,"y":0,"width":340,"height":400})
    b.close()
print("errors:", errs[:5])
