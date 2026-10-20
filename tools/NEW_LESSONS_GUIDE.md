# Writing new lessons for Spark Notebook

Spark Notebook is an offline learning app: short illustrated cards, each with a "Go deeper" deep dive,
and a quiz at the end of each lesson. You are writing complete NEW lessons in English (they are translated later).

Read first:
- tools/lesson_example.txt — a real, published lesson in the exact file format (study the length and tone).
- tools/AGENT_GUIDE.md — the deep-dive rules and the list of diagram kinds with their size limits (applies to card diagrams too).

## File format (see tools/lessontool.py docstring)
```
=== <lesson-id>
title: <lesson title>
summary: <one line, what the lesson covers>

# <card title>
type: concept          (optional: concept | fact | formula | example)
@viz {single-line JSON diagram}
Card text: 2–3 short paragraphs, 25–80 words in total. Each plain line is a paragraph.
---
<the card's deep dive: 8–12 blocks, 200–350 words, 2–3 @viz diagrams, one > key idea, a !! myth or !? fact where natural>

?? Question? | wrong | *right | wrong || One-line explanation.
```
- Exactly 10 cards per lesson, in a sensible teaching order; 3–5 quiz questions at the end of each lesson.
- Card titles: short (2–6 words), unique within the lesson.
- The card text is the "In short" version; the deep dive goes further and must not repeat it.
- Accurate, well-established facts; round numbers with "about"; no invented quotes or statistics.
  Knowledge as of mid-2026. Neutral and balanced on politics and religion.
- Plain, friendly British English. €, metric units, °C.
- Don't reproduce lyrics or poems published after 1928 (describe them instead).

## Tools (run from /home/claude/spark-site)
- `python3 tools/lessontool.py check content/lessons/<file>.lessons.txt` — structure, sizes, missing parts.
- `python3 tools/check_viz.py x content/lessons/<file>.lessons.txt` — renders every diagram (card + deep); fix every problem.
- `python3 tools/lessontool.py export <lesson-id>` — print any existing lesson for reference.
Write ONLY your own files in content/lessons/ (name them `<something>.lessons.txt`). Never edit packs/ or other files.
Finish when both tools report no issues / 0 problems.
