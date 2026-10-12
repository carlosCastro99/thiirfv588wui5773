#!/usr/bin/env python3
"""dump.py <pack> [lesson-id ...] : print lessons, card titles (exact) and card text."""
import json,sys,os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deeptool import SITE
p=json.load(open(os.path.join(SITE,"packs",sys.argv[1]+".json"),encoding="utf-8"))
want=set(sys.argv[2:])
for i,l in enumerate(p["lessons"],1):
    if want and l["id"] not in want: continue
    print(f"\n== {l['id']}   (lesson {i}: {l['title']} — {l.get('summary','')})")
    for c in l["cards"]:
        print(f"# {c['title']}\n   [{c.get('type','')}] {c.get('text','')}")
