#!/usr/bin/env python3
"""Regenerate packs/catalog.json from the pack files.
Base packs: packs/<id>.json. Translations: packs/<lang>/<id>.json.
Pack-level metadata kept in the base file: base (language of the base file, default en),
only (UI languages that see the pack), country (ISO code for country packs), free (free lessons)."""
import os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PK = os.path.join(ROOT, "packs")
LANGS = ["en", "pt-PT", "pt-BR", "es", "fr", "zh"]

def entry(pid, old):
    p = json.load(open(os.path.join(PK, pid + ".json"), encoding="utf-8"))
    ls = p["lessons"]
    e = {"id": pid, "topic": p["topic"], "title": p["title"], "blurb": p["blurb"], "version": p.get("version", 1),
         "lessons": len(ls), "cards": sum(len(l["cards"]) for l in ls), "quiz": sum(len(l.get("quiz", [])) for l in ls),
         "kb": round(os.path.getsize(os.path.join(PK, pid + ".json")) / 1024)}
    base = p.get("base", "en"); e["base"] = base
    for k in ("only", "country", "free"):
        if k in p: e[k] = p[k]
    langs, vers, i18n = [base], {base: e["version"]}, {}
    for lang in LANGS:
        f = os.path.join(PK, lang, pid + ".json")
        if lang == base or not os.path.exists(f): continue
        q = json.load(open(f, encoding="utf-8"))
        langs.append(lang); vers[lang] = q.get("version", 1)
        i18n[lang] = {"title": q["title"], "blurb": q["blurb"]}
    e["langs"] = langs; e["vers"] = vers
    if i18n: e["i18n"] = i18n
    return e

def build():
    cp = os.path.join(PK, "catalog.json")
    old = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else []
    order = [c["id"] for c in old]
    ids = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(PK, "*.json")) if not f.endswith("catalog.json"))
    order = [i for i in order if i in ids] + [i for i in ids if i not in order]
    cat = [entry(i, old) for i in order]
    json.dump(cat, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
    return cat

if __name__ == "__main__":
    for c in build():
        print(f"{c['id']:12} {c['topic']:7} v{c['version']:<3} {c['lessons']:>2}L {c['cards']:>3}C langs={','.join(c['langs'])}{' only='+','.join(c['only']) if 'only' in c else ''}{' country='+c['country'] if 'country' in c else ''}")
