#!/usr/bin/env python3
"""Render every deep-dive diagram with the app's own VZ engine and report
text that overflows the drawing or overlaps other text.
usage: check_viz.py <pack> [deep files...]   (files: check those instead of repo pack)"""
import json, sys, os, threading, http.server, socketserver, functools
sys.path.insert(0, os.path.dirname(__file__))
from deeptool import parse_deep, SITE
from playwright.sync_api import sync_playwright

pid = sys.argv[1]
specs = []
if len(sys.argv) > 2:
    for f in sys.argv[2:]:
        if f.endswith(".lessons.txt"):
            import lessontool
            for L in lessontool.parse_lessons(f):
                for c in L["cards"]:
                    if c.get("viz"): specs.append((f"{L['id']}/{c['title']}#card", c["viz"]))
                    for i, b in enumerate(c.get("deep", [])):
                        if b["t"] == "viz": specs.append((f"{L['id']}/{c['title']}#{i}", b["v"]))
            continue
        for lid, cards in parse_deep(f).items():
            for t, bl in cards.items():
                for i, b in enumerate(bl):
                    if b["t"] == "viz": specs.append((f"{lid}/{t}#{i}", b["v"]))
else:
    p = json.load(open(os.path.join(SITE, "packs", pid + ".json")))   # pid may be "zh/maths"
    for l in p["lessons"]:
        for c in l["cards"]:
            if c.get("viz"): specs.append((f"{l['id']}/{c['title']}#card", c["viz"]))
            for i, b in enumerate(c.get("deep", [])):
                if b["t"] == "viz": specs.append((f"{l['id']}/{c['title']}#{i}", b["v"]))

class _H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
Handler = functools.partial(_H, directory=SITE)
srv = socketserver.TCPServer(("127.0.0.1", 0), Handler)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

JS = r"""
async (specs)=>{
 const out=[]; const host=document.createElement('div');
 host.className='sk paper';host.style.cssText='position:absolute;left:0;top:0;width:340px;background:#fff;z-index:99999';
 document.body.appendChild(host);
 host.innerHTML=VZ({k:'flow',steps:['Warm up fonts','Bold text','more']}); await document.fonts.ready; await new Promise(r=>setTimeout(r,300));
 for(const [name,v] of specs){
  let g; try{g=VZ(v)}catch(e){out.push([name,'error '+e.message]);continue}
  if(!g){out.push([name,'empty']);continue}
  host.innerHTML=g; const svg=host.querySelector('svg'); if(!svg){out.push([name,'no svg']);continue}
  const vb=svg.viewBox.baseVal; svg.style.width=vb.width+'px'; svg.style.height=vb.height+'px'; svg.style.display='block';
  svg.querySelectorAll('[filter]').forEach(e=>e.removeAttribute('filter'));
  const R=svg.getBoundingClientRect();
  const ts=[...svg.querySelectorAll('text')].filter(t=>t.textContent.trim()).map(t=>{const r=t.getBoundingClientRect();return {t:t.textContent.trim(),x0:r.left-R.left,y0:r.top-R.top,x1:r.right-R.left,y1:r.bottom-R.top}});
  const probs=[];
  for(const a of ts){ if(a.x0<-3||a.y0<-3||a.x1>vb.width+3||a.y1>vb.height+3) probs.push('overflow: '+a.t.slice(0,40)) }
  for(let i=0;i<ts.length;i++)for(let j=i+1;j<ts.length;j++){const a=ts[i],b=ts[j];
    const w=Math.min(a.x1,b.x1)-Math.max(a.x0,b.x0), h=Math.min(a.y1,b.y1)-Math.max(a.y0,b.y0);
    if(w>3&&h>4) probs.push('overlap: '+a.t.slice(0,30)+' / '+b.t.slice(0,30)) }
  const tiny=[...svg.querySelectorAll('text')].filter(t=>parseFloat(getComputedStyle(t).fontSize)<9&&t.textContent.trim());
  if(tiny.length) probs.push('tiny text: '+tiny[0].textContent.slice(0,30));
  if(probs.length) out.push([name,probs.slice(0,3).join(' | ')]);
 }
 return out;
}
"""
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 400, "height": 800})
    pg.goto(f"http://127.0.0.1:{port}/index.html")
    pg.wait_for_function("typeof VZ==='function'"); pg.evaluate('document.fonts.ready')
    bad = pg.evaluate(JS, specs)
    b.close()
print(f"{pid}: {len(specs)} diagrams, {len(bad)} with problems")
for n, p in bad: print(" ", n, "->", p)
srv.shutdown()
