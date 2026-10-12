# Writing "Go deeper" deep dives for Spark Notebook

Spark Notebook is an offline learning app. Every card has a short text (~60–90 words).
Tapping **Go deeper** opens a longer explanation: paragraphs, subheadings, bullets,
hand-drawn diagrams, a key idea, myths and facts. You are writing those deep dives.

## Tools (all in tools/)
- `python3 dump.py <pack> <lesson-id> ...` prints each card's EXACT title and its short text.
- `python3 deeptool.py check <pack> <your files...>` parses & validates (titles must match exactly).
- `python3 check_viz.py <pack> <your files...>` renders every diagram with the real app engine
  and lists overflow / overlap / tiny text. Fix every reported problem (shorten labels, fewer items,
  or a different diagram kind), then re-run until it reports 0 problems.
- Do NOT edit anything in the published files (index.html, packs/). Only write your own files in content/deep/ (or a scratch folder).

## File format (UTF-8 text)
```
== <lesson-id>
# <exact card title>
A plain line is a paragraph (2–4 sentences).
### A subheading
• bullet one
• bullet two
> Key idea: one memorable sentence (exactly one per card, near the end).
!! Common myth => What is actually true
!? A surprising "did you know?" fact.
ex: worked step 1 | step 2 | result          (worked example, shown as lines)
= formula or rule written on one line
@viz {single-line JSON diagram, see below}
```
Lines starting with `//` are comments. Every card of every lesson you are assigned needs a deep dive.

## What a good deep dive looks like
- 8–12 blocks, roughly 200–350 words of text, **2–3 diagrams**, 1–3 subheadings, one `>` key idea.
  Add a `!!` myth or `!?` fact when there's a good one (most cards have one of them), `ex:` for anything numeric.
- Go **beyond** the card text: the mechanism (why/how), concrete numbers, dates, names, examples,
  consequences, links to everyday life. Don't repeat the short text; build on it.
- Plain, friendly, clear British English for a curious adult (no jargon without explaining it).
  Short sentences. No filler ("In conclusion", "It's important to note").
- Be ACCURATE. Prefer well-established facts; round numbers and say "about". If a figure is
  uncertain or disputed, say so or leave it out. Don't invent quotes, studies or statistics.
  Knowledge is as of 2026. Use `**bold**` sparingly for a key term.
- Where natural, include a Portugal/Europe angle (the reader is Portuguese), but don't force it.
- Use `€`, metric units, °C.

## Diagram kinds (`@viz` JSON, must be ONE line, valid JSON, double quotes)
Keep text short — the drawing is only 320×180 and labels are hand-lettered.
- flow (3–5 steps, ≤ 28 chars each): `{"k":"flow","steps":["A","B","C"]}`
- cycle (3–5 steps, ≤ 26 chars): `{"k":"cycle","steps":["A","B","C","D"]}`
- stack (3–5 layers, top first, ≤ 32 chars): `{"k":"stack","items":["Top","Middle","Base"]}`
- list (3–5 items, ≤ 34 chars): `{"k":"list","items":["…","…","…"]}`
- tree (root ≤ 24, 3–4 branches ≤ 28): `{"k":"tree","root":"Root","items":["a","b","c"]}`
- cmp (two sides, title ≤ 18, 2–3 items ≤ 24): `{"k":"cmp","l":{"t":"Left","items":["x","y"]},"r":{"t":"Right","items":["x","y"]}}`
- pairs (2–4 rows, a ≤ 22, b ≤ 30): `{"k":"pairs","items":[{"a":"Term","b":"meaning"}]}`
- fix (1–2 rows, wrong → better): `{"k":"fix","items":[{"w":"wrong idea","r":"better idea"}]}`
- time (3–5 events, y ≤ 9 chars, l ≤ 22): `{"k":"time","events":[{"y":"1755","l":"Lisbon earthquake"}]}`
- nums (2–3 big numbers, v ≤ 10 chars, l ≤ 24): `{"k":"nums","items":[{"v":"37 trillion","l":"cells in a body"}]}`
- bars (2–5 bars, labels ≤ 18, values ≥ 0, unit ≤ 30, optional "t" display text, "hi":true highlights one):
  `{"k":"bars","unit":"km/h","items":[{"l":"Cheetah","v":110,"hi":true},{"l":"Human","v":37}]}`
- scale (3–4 points on a line from lo to hi, optional "log":true; unit ≤ 18 chars, labels ≤ 14):
  `{"k":"scale","lo":0,"hi":14,"unit":"pH","items":[{"l":"Lemon","v":2},{"l":"Water","v":7,"hi":true},{"l":"Bleach","v":12.5}]}`
- terms (a formula ≤ 24 chars + 2–4 symbol meanings): `{"k":"terms","f":"F = m × a","items":[{"s":"F","m":"force, N"},{"s":"m","m":"mass, kg"}]}`
Pick the kind that fits the idea; vary kinds across a lesson. Bars/scale must use real or clearly
labelled illustrative values ("(illustrative)" in unit). Avoid superscript-heavy text in diagrams.

## Examples (real, already-published deep dives)
See tools//example.txt.

## Workflow
1. `dump.py` your lessons. 2. Write files of 2 lessons each (`deep/<pack>_<n>.txt`).
3. After each file: `deeptool.py check` then `check_viz.py`; fix until clean.
4. At the end run both tools on ALL your files together and report: files written,
   cards covered (must be all of your lessons' cards), and "0 problems".

## Rules
- Don't reproduce song lyrics, poems or book passages (a few words of a title or a famous short phrase
  is fine; full lines of poems/lyrics only if first published before 1929). Describe instead.
- Health/body topics: general, well-established science; no personal dosing or diet targets.
- Write ONLY in content/deep/ (or a scratch folder) using your own file-name prefix; never touch other agents' files.
