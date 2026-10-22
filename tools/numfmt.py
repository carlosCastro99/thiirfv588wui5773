#!/usr/bin/env python3
"""Localise number formatting inside translated TSVs (values only).
pt-PT, es, fr: decimal comma; thousands with a no-break space from 5 digits (2000, 25 000).
pt-BR: decimal comma; thousands with a point from 4 digits (2.000).
Version numbers and product names are left alone (Web 2.0, GPT-4.5, Python 3.12, 192.168.1.1).
usage: numfmt.py <lang> [--dry] files..."""
import re, sys
NB = " "
SKIP_BEFORE = re.compile(r"(?:[A-Za-z\-_/]|\b(?:Web|Industry|Indústria|Industria|Industrie|Python|iOS|Android|Bluetooth|USB|HTTP|HTML|Wi-?Fi|PCI|Claude|GPT|Llama|Gemini|Windows|macOS|version|versão|versión|v)\s?)$")
THOU = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+)(?:\.(\d+))?(?![\d,]|\.\d)")
DEC = re.compile(r"(?<![\d.,])(\d+)\.(\d+)(?![\d]|\.\d)")

def fix(text, lang):
    def thou(m):
        if SKIP_BEFORE.search(text[:m.start()]): return m.group(0)
        digits = m.group(1).replace(",", "")
        if lang == "pt-BR": grouped = f"{int(digits):,}".replace(",", ".")
        else: grouped = digits if len(digits) <= 4 else f"{int(digits):,}".replace(",", NB)
        return grouped + ("," + m.group(2) if m.group(2) else "")
    text = THOU.sub(thou, text)
    def dec(m):
        before = text[:m.start()]
        if SKIP_BEFORE.search(before): return m.group(0)
        if re.search(r"\d\.\d+\.$", before): return m.group(0)
        return f"{m.group(1)},{m.group(2)}"
    return DEC.sub(dec, text)

if __name__ == "__main__":
    lang = sys.argv[1]; dry = "--dry" in sys.argv
    for f in [a for a in sys.argv[2:] if a != "--dry"]:
        out, n = [], 0
        for line in open(f, encoding="utf-8"):
            if "\t" in line:
                k, v = line.rstrip("\n").split("\t", 1)
                nv = fix(v, lang)
                if nv != v:
                    n += 1
                    if dry and n <= 12: print(f"  {k}: {v[:90]!r}\n   -> {nv[:90]!r}")
                line = f"{k}\t{nv}\n"
            out.append(line)
        if not dry: open(f, "w", encoding="utf-8").write("".join(out))
        print(f"{f}: {n} lines changed")
