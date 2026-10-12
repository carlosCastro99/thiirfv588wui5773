#!/usr/bin/env python3
"""Export the deep dives stored in packs/*.json back to the text format
(content/deep/<pack>.txt), and verify the round trip.
usage: export_deep.py [pack ...]   (default: all packs)"""
import json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deeptool import SITE, parse_deep, norm_viz

OUT = os.path.join(SITE, "content", "deep")


def viz_line(v):
    v = json.loads(json.dumps(v))
    if v["k"] in ("bars", "scale"):
        for it in v["items"]:
            if not it.get("hi"): it.pop("hi", None)
            if it.get("t") == f"{float(it['v']):g}": it.pop("t", None)
        if v["k"] == "scale" and not v.get("log"): v.pop("log", None)
    return "@viz " + json.dumps(v, ensure_ascii=False)


def block_lines(b):
    t = b["t"]
    if t == "p": return [b["x"]]
    if t == "h": return ["### " + b["x"]]
    if t == "ul": return ["• " + x for x in b["x"]]
    if t == "key": return ["> " + b["x"]]
    if t == "myth": return [f"!! {b['w']} => {b['r']}"]
    if t == "fact": return ["!? " + b["x"]]
    if t == "ex": return ["ex: " + " | ".join(b["x"])]
    if t == "f": return ["= " + b["x"]]
    if t == "viz": return [viz_line(b["v"])]
    raise SystemExit(f"unknown block {t}")


def export(pid):
    p = json.load(open(os.path.join(SITE, "packs", pid + ".json"), encoding="utf-8"))
    out = [f"// Deep dives for pack '{pid}' (exported from packs/{pid}.json)"]
    for l in p["lessons"]:
        out += ["", f"== {l['id']}"]
        for c in l["cards"]:
            if not c.get("deep"): continue
            out += ["", f"# {c['title']}"]
            prev = None
            for b in c["deep"]:
                if b["t"] == "ul" and prev == "ul":
                    raise SystemExit("two lists in a row cannot be represented")
                out += block_lines(b); prev = b["t"]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, pid + ".txt")
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    # round trip
    back = parse_deep(path)
    n = 0
    for l in p["lessons"]:
        for c in l["cards"]:
            if not c.get("deep"): continue
            want = json.loads(json.dumps(c["deep"]))
            for b in want:
                if b["t"] == "viz": norm_viz(b["v"], "orig")
            got = back[l["id"]][c["title"]]
            if json.dumps(got, sort_keys=True) != json.dumps(want, sort_keys=True):
                raise SystemExit(f"round trip mismatch: {l['id']} / {c['title']}")
            n += 1
    print(f"{pid}: {n} deep dives -> content/deep/{pid}.txt (round trip OK)")


packs = sys.argv[1:] or sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(SITE, "packs", "*.json")) if not f.endswith("catalog.json"))
for pid in packs: export(pid)
