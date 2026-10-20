#!/usr/bin/env python3
"""One-off: create the Portugal country pack and give History/World/Nature/Art global replacements.

Moves hi-discovery, hi-portugal, hi-pt20 (History), wo-portugal (World), na-portugal (Nature),
ar-portugal (Art) into packs/portugal.json together with the 14 new pt-* lessons, and puts the new
global lessons in their place. Lesson ids never change, so progress and favourites survive.
usage: restructure_portugal.py content/lessons/*.lessons.txt
"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lessontool import parse_lessons, validate
from deeptool import SITE
PK = os.path.join(SITE, "packs")

PORTUGAL_ORDER = ["wo-portugal", "hi-portugal", "hi-discovery", "pt-lisbon", "pt-porto", "pt-islands", "pt-language",
                  "pt-lusophone", "hi-pt20", "pt-democracy", "pt-economy", "pt-sea", "na-portugal", "pt-food", "pt-fado",
                  "ar-portugal", "pt-architecture", "pt-science", "pt-traditions", "pt-sport"]
HISTORY_ORDER = ["hi-turns", "hi-egypt", "hi-greece", "hi-china", "hi-rome", "hi-medieval", "hi-andalus", "hi-mongols",
                 "hi-americas", "hi-renaissance", "hi-reform", "hi-1755", "hi-revolutions", "hi-19c", "hi-ww1",
                 "hi-interwar", "hi-ww2", "hi-coldwar", "hi-modern", "hi-digital"]
REPLACE = {"world": ("wo-portugal", "wo-poles"), "nature": ("na-portugal", "na-fungi"), "art": ("ar-portugal", "ar-asia")}

def load(pid): return json.load(open(os.path.join(PK, pid + ".json"), encoding="utf-8"))
def save(p):
    p["version"] = p.get("version", 1) + 1
    open(os.path.join(PK, p["id"] + ".json"), "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False))
    print(f"{p['id']}: v{p['version']}, {len(p['lessons'])} lessons")

new = {}
for f in sys.argv[1:]:
    for L in parse_lessons(f):
        iss = validate(L)
        if iss: raise SystemExit(f"{L['id']}: {iss}")
        new[L["id"]] = L
need = [i for i in PORTUGAL_ORDER + HISTORY_ORDER + [b for _, b in REPLACE.values()] if i.startswith(("pt-",)) or i in ("hi-china", "hi-mongols", "hi-americas", "wo-poles", "na-fungi", "ar-asia")]
missing = [i for i in need if i not in new]
if missing: raise SystemExit(f"missing new lessons: {missing}")

existing = {}
for pid in ("history", "world", "nature", "art"):
    for l in load(pid)["lessons"]: existing[l["id"]] = l
pool = {**existing, **new}

if os.path.exists(os.path.join(PK, "portugal.json")): raise SystemExit("portugal.json already exists")
portugal = {"id": "portugal", "topic": "c-pt", "title": "Portugal", "version": 0, "country": "PT", "free": 1,
            "blurb": "History, places, food, music and nature of Portugal, from the Algarve to the Azores.",
            "lessons": [pool[i] for i in PORTUGAL_ORDER]}
save(portugal)
h = load("history"); h["lessons"] = [pool[i] for i in HISTORY_ORDER]
h["blurb"] = "The turning points of humanity, from the first farmers to the digital age."; save(h)
for pid, (old, rep) in REPLACE.items():
    p = load(pid); p["lessons"] = [pool[rep] if l["id"] == old else l for l in p["lessons"]]; save(p)
for pid in ("history", "world", "nature", "art", "portugal"):
    assert len(load(pid)["lessons"]) == 20, pid
