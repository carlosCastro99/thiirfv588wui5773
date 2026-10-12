import threading,http.server,socketserver,functools,sys
from playwright.sync_api import sync_playwright
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deeptool import SITE
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
s=socketserver.TCPServer(("127.0.0.1",0),functools.partial(H,directory=SITE));threading.Thread(target=s.serve_forever,daemon=True).start()
packs=sys.argv[1:]
with sync_playwright() as pw:
  b=pw.chromium.launch();pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
  errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
  pg.goto(f"http://127.0.0.1:{s.server_address[1]}/index.html");pg.wait_for_timeout(800)
  # dismiss onboarding if present
  pg.evaluate("async ids=>{await doDownload(ids)}",packs); pg.wait_for_timeout(500)
  n=pg.evaluate("Object.keys(PACKS).length"); print("packs loaded",n)
  for p in packs:
    r=pg.evaluate("""p=>{const pk=PACKS[p];if(!pk)return 'missing';const cs=pk.lessons.flatMap(l=>l.cards);return [pk.version,cs.length,cs.filter(c=>c.deep).length]}""",p); print(p,r)
  res=pg.evaluate("""ps=>{let n=0,bad=[];for(const id of Object.keys(CARDS)){const c=CARDS[id];if(!ps.includes(PACKS[LESSONS[c.lesson].pack].id))continue;try{openDeep(id);const el=document.querySelector('#deep');if(el.hidden||!el.querySelector('.dsec, .dlead, p'))bad.push(id);n++;closeDeep()}catch(e){bad.push(id+':'+e.message)}}return [n,bad.slice(0,5)]}""",packs); print("opened",res)
  for i,(lid) in enumerate(["hi-1755-c1","ma-prob-c3","ph-ethics-c0"]):
    pg.evaluate("id=>openDeep(id)",lid); pg.wait_for_timeout(700); pg.screenshot(path=f"/tmp/e2e_{i}.png"); pg.evaluate("closeDeep()")
  print("errors:",errs[:3]); b.close()
