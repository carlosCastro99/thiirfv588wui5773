#!/usr/bin/env python3
"""Assemble index.html from src/app.html + src/fonts/*.b64 + packs/catalog.json,
and bump the service-worker cache name. usage: build.py"""
import os, re, json, hashlib, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def build():
    catalog.build()
    t = open(os.path.join(ROOT, "src", "app.html"), encoding="utf-8").read()
    for f in glob.glob(os.path.join(ROOT, "src", "fonts", "*.b64")):
        n = os.path.basename(f)[:-4]
        t = t.replace(f"/*FONT:{n}*/", open(f).read().strip())
    assert "/*FONT:" not in t, "missing font"
    cat = json.load(open(os.path.join(ROOT, "packs", "catalog.json"), encoding="utf-8"))
    t = t.replace("/*CATALOG*/", json.dumps(cat, ensure_ascii=False))
    for name in ("i18n.js",):
        p = os.path.join(ROOT, "src", name)
        if os.path.exists(p):
            t = t.replace(f"/*INCLUDE:{name}*/", open(p, encoding="utf-8").read())
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
    sp = os.path.join(ROOT, "sw.js"); sw = open(sp).read()
    h = int(hashlib.md5(t.encode()).hexdigest()[:8], 16) % 10**8
    sw = re.sub(r"const CACHE='spark-[^']*'", f"const CACHE='spark-{h}'", sw)
    open(sp, "w").write(sw)
    return len(t)
if __name__ == "__main__":
    print("index.html", build(), "bytes")
