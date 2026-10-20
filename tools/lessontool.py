#!/usr/bin/env python3
"""Whole lessons (cards + diagrams + deep dives + quiz) in one text format.

  lessontool.py export <lesson-id> [...]     print existing lessons in the format (for reference)
  lessontool.py check <files...>             parse + validate (structure, sizes, diagrams JSON)

Format (one file may hold several lessons):
  === <lesson-id>
  title: <lesson title>
  summary: <one line>

  # <card title>
  type: concept            (optional: concept | fact | formula | example; default concept)
  formula: V = I × R       (optional, shown big under the title)
  @viz {single-line JSON}  (the card's diagram, same kinds as deep dives; required)
  First paragraph of the card text.
  Second paragraph.        (each plain line is a paragraph; "• " lines are bullets)
  example: step | step | result   (optional worked example lines)
  ---
  <deep dive in the deep-dive format: paragraphs, ### heads, • bullets, > key, !! myth => reality, !? fact, ex:, =, @viz>

  ?? Question? | wrong option | *right option | wrong option || One-line explanation.
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deeptool import norm_viz, SITE
import deeptool

def parse_lessons(path):
    lessons, L, card, mode, deep_lines = [], None, None, None, []
    def close_card():
        nonlocal card, deep_lines
        if card is not None:
            if deep_lines:
                tmp = os.path.join(os.path.dirname(os.path.abspath(path)), ".__deep_tmp.txt")
                open(tmp, "w", encoding="utf-8").write(f"== {L['id']}\n# {card['title']}\n" + "\n".join(deep_lines) + "\n")
                try: card["deep"] = deeptool.parse_deep(tmp)[L["id"]][card["title"]]
                finally: os.remove(tmp)
            blocks = card.pop("_text")
            card["text"] = "\n\n".join(blocks)
            L["cards"].append(card)
        card, deep_lines = None, []
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.rstrip("\n").strip(); where = f"{os.path.basename(path)}:{n}"
        if line.startswith("=== "):
            close_card()
            L = {"id": line[4:].strip(), "title": "", "summary": "", "cards": [], "quiz": []}; lessons.append(L); mode = "head"; continue
        if L is None:
            if line and not line.startswith("//"): raise SystemExit(f"{where}: text before the first === lesson")
            continue
        if line.startswith("?? "):
            close_card(); mode = "quiz"
            body, _, ex = line[3:].partition("||")
            parts = [p.strip() for p in body.split("|")]
            q, opts = parts[0], parts[1:]
            ans = [i for i, o in enumerate(opts) if o.startswith("*")]
            if len(opts) < 2 or len(ans) != 1: raise SystemExit(f"{where}: quiz needs 2+ options and exactly one *correct")
            L["quiz"].append({"q": q, "options": [o.lstrip("*").strip() for o in opts], "answer": ans[0], "explain": ex.strip()})
            continue
        if line.startswith("# ") and not line.startswith("### "):
            close_card(); card = {"type": "concept", "title": line[2:].strip(), "_text": []}; mode = "card"; continue
        if mode == "head":
            if line.startswith("title:"): L["title"] = line[6:].strip()
            elif line.startswith("summary:"): L["summary"] = line[8:].strip()
            elif line and not line.startswith("//"): raise SystemExit(f"{where}: expected title:/summary:/# card")
            continue
        if mode == "card":
            if line == "---": mode = "deep"; continue
            if not line or line.startswith("//"): continue
            if line.startswith("type:"): card["type"] = line[5:].strip(); continue
            if line.startswith("formula:"): card["formula"] = line[8:].strip(); continue
            if line.lower().startswith("example:"): card["example"] = [s.strip() for s in line[8:].split("|") if s.strip()]; continue
            if line.startswith("@viz"):
                try: card["viz"] = norm_viz(json.loads(line[4:].strip()), where)
                except json.JSONDecodeError as e: raise SystemExit(f"{where}: bad viz JSON: {e}")
                continue
            if line.startswith("• ") and card["_text"]: card["_text"][-1] += "\n" + line
            else: card["_text"].append(line)
            continue
        if mode == "deep":
            deep_lines.append(line); continue
        if mode == "quiz" and line and not line.startswith("//"):
            raise SystemExit(f"{where}: unexpected text after the quiz")
    close_card()
    return lessons

def words(s): return len(re.findall(r"\w+", s))

def validate(L, cards_per=10):
    issues = []
    if not L["title"] or not L["summary"]: issues.append("missing title/summary")
    if len(L["cards"]) != cards_per: issues.append(f"{len(L['cards'])} cards (need {cards_per})")
    if len(L["quiz"]) < 3: issues.append(f"{len(L['quiz'])} quiz questions (need 3+)")
    for c in L["cards"]:
        t = c["title"]
        if c["type"] not in ("concept", "fact", "formula", "example"): issues.append(f"{t}: bad type {c['type']}")
        if "viz" not in c: issues.append(f"{t}: no @viz")
        w = words(c["text"])
        if not 18 <= w <= 110: issues.append(f"{t}: card text {w} words (18–110)")
        d = c.get("deep", [])
        if len(d) < 7: issues.append(f"{t}: deep dive only {len(d)} blocks")
        if sum(1 for b in d if b["t"] == "viz") < 2: issues.append(f"{t}: deep dive needs 2+ diagrams")
        if not any(b["t"] == "key" for b in d): issues.append(f"{t}: deep dive has no > key idea")
    return issues

def to_dsl(L):
    from export_deep import block_lines, viz_line
    out = [f"=== {L['id']}", f"title: {L['title']}", f"summary: {L['summary']}"]
    for c in L["cards"]:
        out += ["", f"# {c['title']}"]
        if c.get("type", "concept") != "concept": out.append(f"type: {c['type']}")
        if c.get("formula"): out.append(f"formula: {c['formula']}")
        if c.get("viz"): out.append(viz_line(c["viz"]))
        for para in c["text"].split("\n\n"): out += para.split("\n")
        if c.get("example"): out.append("example: " + " | ".join(c["example"]))
        out.append("---")
        for b in c.get("deep", []): out += block_lines(b)
    out.append("")
    for q in L.get("quiz", []):
        opts = " | ".join(("*" if i == q["answer"] else "") + o for i, o in enumerate(q["options"]))
        out.append(f"?? {q['q']} | {opts} || {q['explain']}")
    return "\n".join(out)

def find_lesson(lid):
    import glob
    for f in glob.glob(os.path.join(SITE, "packs", "*.json")):
        if f.endswith("catalog.json"): continue
        for l in json.load(open(f, encoding="utf-8"))["lessons"]:
            if l["id"] == lid: return l
    raise SystemExit(f"no lesson {lid}")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        for lid in sys.argv[2:]: print(to_dsl(find_lesson(lid))); print()
    elif cmd == "check":
        bad = 0
        for f in sys.argv[2:]:
            for L in parse_lessons(f):
                iss = validate(L); bad += len(iss)
                print(f"{L['id']}: {len(L['cards'])} cards, {len(L['quiz'])} quiz, {sum(len(c.get('deep',[])) for c in L['cards'])} deep blocks" + ("" if not iss else "  ISSUES: " + "; ".join(iss)))
        sys.exit(1 if bad else 0)
