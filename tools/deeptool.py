#!/usr/bin/env python3
"""Parse deep-dive DSL files and attach them to a pack in the site repo.

DSL (one file may cover several lessons):
  == <lesson-id>
  # <exact card title>
  Plain line                 -> paragraph
  ### Subheading             -> heading
  • item  (or "- item")      -> bullet list (consecutive lines)
  > text                     -> key idea
  !! myth => reality         -> myth / reality
  !? text                    -> did you know
  ex: step | step | step     -> worked example (lines)
  = formula                  -> formula
  @viz {json}                -> diagram (single-line JSON)

usage: deeptool.py check <pack> files...      (parse+validate only)
       deeptool.py attach <pack> files...     (write into repo, bump version)
"""
import json, sys, os, re, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SITE = os.environ.get("SITE", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VIZ_REQ = {
    "flow": ["steps"], "cycle": ["steps"], "stack": ["items"], "list": ["items"],
    "tree": ["root", "items"], "cmp": ["l", "r"], "pairs": ["items"], "fix": ["items"],
    "time": ["events"], "nums": ["items"], "bars": ["items"], "scale": ["items", "lo", "hi"],
    "terms": ["f", "items"],
}


def norm_viz(v, where):
    k = v.get("k")
    if k not in VIZ_REQ:
        raise SystemExit(f"{where}: unknown viz kind {k!r}")
    for f in VIZ_REQ[k]:
        if f not in v:
            raise SystemExit(f"{where}: viz {k} missing {f!r}")
    if k in ("bars", "scale"):
        for it in v["items"]:
            if "l" not in it or "v" not in it:
                raise SystemExit(f"{where}: {k} item needs l and v: {it}")
            if not isinstance(it["v"], (int, float)):
                raise SystemExit(f"{where}: {k} value must be a number: {it}")
            it["v"] = float(it["v"])
            it.setdefault("t", (f"{it['v']:g}"))
            it["t"] = str(it["t"])
            it["hi"] = bool(it.get("hi", False))
        v.setdefault("unit", "")
        if k == "scale":
            v["lo"] = float(v["lo"]); v["hi"] = float(v["hi"]); v["log"] = bool(v.get("log", False))
        if k == "bars" and any(it["v"] < 0 for it in v["items"]):
            raise SystemExit(f"{where}: bars cannot be negative")
    if k == "cmp":
        for s in ("l", "r"):
            if "t" not in v[s] or "items" not in v[s]:
                raise SystemExit(f"{where}: cmp side needs t and items")
    if k == "pairs":
        for it in v["items"]:
            if "a" not in it or "b" not in it: raise SystemExit(f"{where}: pairs item needs a,b")
    if k == "fix":
        for it in v["items"]:
            if "w" not in it or "r" not in it: raise SystemExit(f"{where}: fix item needs w,r")
    if k == "time":
        for it in v["events"]:
            if "y" not in it or "l" not in it: raise SystemExit(f"{where}: time event needs y,l")
            it["y"] = str(it["y"])
    if k == "nums":
        for it in v["items"]:
            if "v" not in it or "l" not in it: raise SystemExit(f"{where}: nums item needs v,l")
            it["v"] = str(it["v"])
    if k == "terms":
        for it in v["items"]:
            if "s" not in it or "m" not in it: raise SystemExit(f"{where}: terms item needs s,m")
    for f in ("steps", "items"):
        if f in v and k in ("flow", "cycle", "stack", "list", "tree"):
            if not all(isinstance(x, str) for x in v[f]):
                raise SystemExit(f"{where}: {k}.{f} must be strings")
    return v


def parse_deep(path):
    out = {}  # lesson -> {title: blocks}
    lesson = card = None
    blocks = None
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.strip()
        where = f"{os.path.basename(path)}:{n}"
        if not line or line.startswith("//"):
            continue
        if line.startswith("== "):
            lesson = line[3:].strip(); out.setdefault(lesson, {}); card = None; continue
        if line.startswith("# ") and not line.startswith("### "):
            if lesson is None: raise SystemExit(f"{where}: card before lesson")
            card = line[2:].strip()
            if card in out[lesson]: raise SystemExit(f"{where}: duplicate card {card!r}")
            blocks = out[lesson][card] = []; continue
        if blocks is None:
            raise SystemExit(f"{where}: content before a card title")
        if line.startswith("### "):
            blocks.append({"t": "h", "x": line[4:].strip()})
        elif line[:2] in ("• ", "- ") or line.startswith("* "):
            item = line[2:].strip()
            if blocks and blocks[-1]["t"] == "ul": blocks[-1]["x"].append(item)
            else: blocks.append({"t": "ul", "x": [item]})
        elif line.startswith("> "):
            blocks.append({"t": "key", "x": line[2:].strip()})
        elif line.startswith("!! "):
            if "=>" not in line: raise SystemExit(f"{where}: myth needs =>")
            w, r = line[3:].split("=>", 1)
            blocks.append({"t": "myth", "w": w.strip(), "r": r.strip()})
        elif line.startswith("!? "):
            blocks.append({"t": "fact", "x": line[3:].strip()})
        elif line.lower().startswith("ex:"):
            blocks.append({"t": "ex", "x": [s.strip() for s in line[3:].split("|") if s.strip()]})
        elif line.startswith("= "):
            blocks.append({"t": "f", "x": line[2:].strip()})
        elif line.startswith("@viz"):
            try: v = json.loads(line[4:].strip())
            except Exception as e: raise SystemExit(f"{where}: bad viz JSON: {e}")
            blocks.append({"t": "viz", "v": norm_viz(v, where)})
        elif line.startswith("@"):
            raise SystemExit(f"{where}: unknown directive {line[:20]}")
        else:
            blocks.append({"t": "p", "x": line})
    return out


def load_pack(pid):
    return json.load(open(os.path.join(SITE, "packs", pid + ".json"), encoding="utf-8"))


def merge(pack, deep):
    lessons = {l["id"]: l for l in pack["lessons"]}
    n = 0
    for lid, cards in deep.items():
        if lid not in lessons: raise SystemExit(f"unknown lesson {lid}")
        titles = {c["title"]: c for c in lessons[lid]["cards"]}
        for t, bl in cards.items():
            if t not in titles:
                raise SystemExit(f"{lid}: no card {t!r}. Titles: {list(titles)}")
            if len(bl) < 3: raise SystemExit(f"{lid}/{t}: too short ({len(bl)} blocks)")
            titles[t]["deep"] = bl; n += 1
    return n


def write_site(pack):
    pid = pack["id"]
    pack["version"] = pack.get("version", 1) + 1
    s = json.dumps(pack, ensure_ascii=False)
    p = os.path.join(SITE, "packs", pid + ".json")
    open(p, "w", encoding="utf-8").write(s)
    kb = round(len(s.encode()) / 1024)
    import build as _b
    _b.build()
    return pack["version"], kb


def main():
    cmd, pid, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    pack = load_pack(pid)
    total = 0
    touched = set()
    for f in files:
        d = parse_deep(f)
        touched |= set(d)
        total += merge(pack, d)
    for l in pack["lessons"]:
        if l["id"] in touched:
            miss = [c["title"] for c in l["cards"] if not c.get("deep")]
            got = sum(1 for c in l["cards"] if c.get("deep"))
            print(f"  {l['id']}: {got}/{len(l['cards'])}" + (f"  MISSING: {miss}" if miss else ""))
    cards = [c for l in pack["lessons"] for c in l["cards"]]
    have = sum(1 for c in cards if c.get("deep"))
    missing = [(l["id"], c["title"]) for l in pack["lessons"] for c in l["cards"] if not c.get("deep")]
    print(f"{pid}: attached {total}; coverage {have}/{len(cards)}")
    if missing and len(missing) <= 40:
        for m in missing: print("  missing:", *m)
    if cmd == "attach":
        v, kb = write_site(pack)
        print(f"{pid}: version {v}, {kb} kB")


if __name__ == "__main__":
    main()
