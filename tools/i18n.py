#!/usr/bin/env python3
"""Translation pipeline for pack content.

  i18n.py extract <pack> [--deep] [--lessons a,b]  -> content/i18n/src/<pack>[.deep].tsv (key<TAB>text)
  i18n.py check <lang> <files...>                   -> validate translated TSVs against the source
  i18n.py apply <lang> [packs...]                   -> build packs/<lang>/<id>.json from all TSVs of <lang>

Keys are stable and lesson-scoped (e.g. hi-turns.c3.text), so a lesson keeps its translation
when it moves to another pack. Newlines inside a text are written as the two characters \\n.
"""
import os, re, sys, json, glob, html, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PK = os.path.join(ROOT, "packs"); CT = os.path.join(ROOT, "content", "i18n")
LANGS = ["pt-PT", "pt-BR", "es", "fr", "zh"]
TXT = re.compile(r"(<text\b[^>]*>)(.*?)(</text>)", re.S)
LETTER = re.compile(r"[^\W\d_]", re.U)

def esc(s): return s.replace("\\", "\\\\").replace("\t", " ").replace("\n", "\\n")
def unesc(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            n = s[i + 1]; out.append("\n" if n == "n" else n); i += 2
        else: out.append(s[i]); i += 1
    return "".join(out)

def viz_strings(v, path=""):
    """yield (path, string) for translatable leaves of a diagram spec"""
    if isinstance(v, dict):
        for k, x in v.items():
            if k in ("k", "hi", "log", "lo"): continue
            yield from viz_strings(x, f"{path}.{k}" if path else k)
    elif isinstance(v, list):
        for i, x in enumerate(v): yield from viz_strings(x, f"{path}.{i}")
    elif isinstance(v, str) and LETTER.search(v):
        yield path, v

def set_path(obj, path, val):
    parts = path.split("."); cur = obj
    for p in parts[:-1]: cur = cur[int(p)] if isinstance(cur, list) else cur[p]
    last = parts[-1]
    if isinstance(cur, list): cur[int(last)] = val
    else: cur[last] = val

def deep_units(c, b):
    for di, d in enumerate(c.get("deep", [])):
        t = d["t"]
        if t in ("p", "h", "key", "fact", "f"): yield f"{b}.d{di}.x", d["x"]
        elif t in ("ul", "ex"):
            for j, x in enumerate(d["x"]): yield f"{b}.d{di}.x.{j}", x
        elif t == "myth": yield f"{b}.d{di}.w", d["w"]; yield f"{b}.d{di}.r", d["r"]
        elif t == "viz":
            for p, s in viz_strings(d["v"]): yield f"{b}.d{di}.v.{p}", s

def units(pack, deep=False, lessons=None):
    """yield (key, text) for one pack"""
    eng = pack["id"] == "english"
    if not lessons:
        yield "P.title", pack["title"]; yield "P.blurb", pack["blurb"]
    for l in pack["lessons"]:
        lid = l["id"]
        if lessons and lid not in lessons: continue
        if not deep:
            yield f"{lid}.title", l["title"]; yield f"{lid}.summary", l["summary"]
            for qi, q in enumerate(l.get("quiz", [])):
                yield f"{lid}.q{qi}.q", q["q"]
                for oi, o in enumerate(q["options"]): yield f"{lid}.q{qi}.o{oi}", o
                yield f"{lid}.q{qi}.x", q["explain"]
        for ci, c in enumerate(l["cards"]):
            b = f"{lid}.c{ci}"
            if deep:
                yield from deep_units(c, b)
                continue
            yield f"{b}.title", c["title"]; yield f"{b}.text", c["text"]
            if c.get("tag"): yield f"{b}.tag", c["tag"]
            if c.get("formula") and LETTER.search(c["formula"]): yield f"{b}.formula", c["formula"]
            for j, x in enumerate(c.get("example", [])): yield f"{b}.example.{j}", x
            if c.get("viz"):
                for p, s in viz_strings(c["viz"]): yield f"{b}.viz.{p}", s
            if c.get("sketch"):
                for j, m in enumerate(TXT.finditer(c["sketch"])):
                    s = html.unescape(m.group(2)).strip()
                    if LETTER.search(s): yield f"{b}.sketch.{j}", s
            if eng and c.get("items"):   # [english word, meaning, note, english example]
                for j, it in enumerate(c["items"]):
                    if len(it) > 1 and it[1]: yield f"{b}.items.{j}.1", it[1]
                    if len(it) > 2 and it[2]: yield f"{b}.items.{j}.2", it[2]

def load_pack(pid): return json.load(open(os.path.join(PK, pid + ".json"), encoding="utf-8"))

def extract(pid, deep=False, lessons=None):
    p = load_pack(pid); os.makedirs(os.path.join(CT, "src"), exist_ok=True)
    name = pid + (".deep" if deep else "") + (("." + "_".join(sorted(lessons))) if lessons else "")
    f = os.path.join(CT, "src", name + ".tsv")
    rows = list(units(p, deep, lessons))
    open(f, "w", encoding="utf-8").write("".join(f"{k}\t{esc(v)}\n" for k, v in rows))
    print(f"{f}: {len(rows)} strings, {sum(len(v) for _, v in rows)} chars")

def read_tsv(f, strict=True):
    d = {}
    for n, line in enumerate(open(f, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"): continue
        if "\t" not in line:
            if strict: raise SystemExit(f"{f}:{n}: no TAB")
            continue
        k, v = line.split("\t", 1)
        d[k.strip()] = unesc(v.strip())
    return d

def source_map():
    src = {}
    for f in glob.glob(os.path.join(PK, "*.json")):
        if f.endswith("catalog.json"): continue
        p = json.load(open(f, encoding="utf-8"))
        for deep in (False, True):
            for k, v in units(p, deep): src[(p["id"], k) if k.startswith("P.") else k] = v
    return src

def problems(k, s, t):
    out = []
    if not t.strip() and s.strip(): out.append("empty")
    if s.count("\n") != t.count("\n"): out.append(f"line breaks {s.count(chr(10))}→{t.count(chr(10))}")
    if s.count("**") != t.count("**"): out.append("bold markers differ")
    if s.count("• ") != t.count("• "): out.append("bullets differ")
    if ".viz." in k or ".v." in k or ".sketch." in k:
        w = sum(2.25 if re.match(r"[⺀-鿿＀-￯]", ch) else 1 for ch in t)
        if w > max(8, len(s) * 1.6 + 4): out.append(f"diagram label too long ({len(s)}→{round(w)})")
    return out

def check(lang, files):
    src = source_map(); bad = 0; n = 0
    for f in files:
        pid = os.path.basename(f).split(".")[0]
        d = read_tsv(f)
        for k, v in d.items():
            sk = (pid, k) if k.startswith("P.") else k
            if sk not in src: print(f"{f}: unknown key {k}"); bad += 1; continue
            for pr in problems(k, src[sk], v): print(f"{f}: {k}: {pr}"); bad += 1
            n += 1
        sf = os.path.join(CT, "src", os.path.basename(f))
        if os.path.exists(sf):
            miss = [k for k in read_tsv(sf) if k not in d]
            if miss: print(f"{f}: {len(miss)} of {len(read_tsv(sf))} strings not translated yet (first: {miss[0]})"); bad += 1
    print(f"{lang}: {n} strings checked, {bad} problems")
    return bad

def apply(lang, only=None):
    tr = {}
    for f in sorted(glob.glob(os.path.join(CT, lang, "*.tsv"))):
        pid = os.path.basename(f).split(".")[0]
        for k, v in read_tsv(f, strict=False).items(): tr[(pid, k) if k.startswith("P.") else k] = v
    os.makedirs(os.path.join(PK, lang), exist_ok=True)
    for f in sorted(glob.glob(os.path.join(PK, "*.json"))):
        if f.endswith("catalog.json"): continue
        p = json.load(open(f, encoding="utf-8")); pid = p["id"]
        if only and pid not in only: continue
        if p.get("base", "en") == lang: continue
        if p.get("only") and lang not in p["only"]: continue
        need = list(units(p, False)); miss = [k for k, _ in need if ((pid, k) if k.startswith("P.") else k) not in tr]
        if miss:
            if len(miss) < len(need): print(f"{pid}: {len(need)-len(miss)}/{len(need)} card strings translated, not built (first missing: {miss[0]})")
            stale = os.path.join(PK, lang, pid + ".json")
            if os.path.exists(stale): os.remove(stale); print(f"  removed stale {lang}/{pid}.json")
            continue
        q = json.loads(json.dumps(p)); q["lang"] = lang; q.pop("only", None)
        g = lambda k: tr[(pid, k) if k.startswith("P.") else k]
        q["title"] = g("P.title"); q["blurb"] = g("P.blurb")
        deep_done = deep_total = 0
        for l in q["lessons"]:
            lid = l["id"]; l["title"] = g(f"{lid}.title"); l["summary"] = g(f"{lid}.summary")
            for qi, qq in enumerate(l.get("quiz", [])):
                qq["q"] = g(f"{lid}.q{qi}.q"); qq["options"] = [g(f"{lid}.q{qi}.o{oi}") for oi in range(len(qq["options"]))]; qq["explain"] = g(f"{lid}.q{qi}.x")
            for ci, c in enumerate(l["cards"]):
                b = f"{lid}.c{ci}"
                c["title"] = g(f"{b}.title"); c["text"] = g(f"{b}.text")
                if c.get("tag"): c["tag"] = g(f"{b}.tag")
                if f"{b}.formula" in tr: c["formula"] = tr[f"{b}.formula"]
                if c.get("example"): c["example"] = [g(f"{b}.example.{j}") for j in range(len(c["example"]))]
                if c.get("viz"):
                    for path, _ in list(viz_strings(c["viz"])): set_path(c["viz"], path, g(f"{b}.viz.{path}"))
                if c.get("sketch"):
                    idx = [0]
                    def sub(m):
                        j = idx[0]; idx[0] += 1; k = f"{b}.sketch.{j}"
                        return m.group(1) + html.escape(tr[k], quote=False) + m.group(3) if k in tr else m.group(0)
                    c["sketch"] = TXT.sub(sub, c["sketch"])
                if c.get("items"):
                    for j, it in enumerate(c["items"]):
                        for x in (1, 2):
                            k = f"{b}.items.{j}.{x}"
                            if k in tr: it[x] = tr[k]
                # deep dive: translated only when every string of the card is present
                if c.get("deep"):
                    deep_total += 1
                    dk = list(deep_units(c, b))
                    if all(k in tr for k, _ in dk):
                        for di, d in enumerate(c["deep"]):
                            t = d["t"]; pre = f"{b}.d{di}"
                            if t in ("p", "h", "key", "fact", "f"): d["x"] = tr[f"{pre}.x"]
                            elif t in ("ul", "ex"): d["x"] = [tr[f"{pre}.x.{j}"] for j in range(len(d["x"]))]
                            elif t == "myth": d["w"] = tr[f"{pre}.w"]; d["r"] = tr[f"{pre}.r"]
                            elif t == "viz":
                                for path, _ in list(viz_strings(d["v"])): set_path(d["v"], path, tr[f"{pre}.v.{path}"])
                        deep_done += 1
                    else:
                        c["dl"] = p.get("base", "en")
        out = os.path.join(PK, lang, pid + ".json")
        body = json.dumps(q, ensure_ascii=False, sort_keys=True)
        h = hashlib.md5(body.encode()).hexdigest()[:10]
        old = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None
        q["version"] = (old.get("version", 1) + (1 if old.get("hash") != h else 0)) if old else 1
        q["hash"] = h
        open(out, "w", encoding="utf-8").write(json.dumps(q, ensure_ascii=False))
        print(f"{lang}/{pid}: v{q['version']}, deep dives translated {deep_done}/{deep_total}")

def p_card(p, lid, ci):
    for l in p["lessons"]:
        if l["id"] == lid: return l["cards"][ci]

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "extract":
        args = sys.argv[2:]; deep = "--deep" in args; les = None
        if "--lessons" in args: les = set(args[args.index("--lessons") + 1].split(","))
        for pid in [a for a in args if not a.startswith("--") and (not les or a not in ",".join(les))]:
            extract(pid, deep, les)
    elif cmd == "check": sys.exit(1 if check(sys.argv[2], sys.argv[3:]) else 0)
    elif cmd == "apply": apply(sys.argv[2], set(sys.argv[3:]) or None)
