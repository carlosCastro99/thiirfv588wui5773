# Translating Spark Notebook content

Each line of a source file is `key<TAB>text`. Write the same keys, in the same order, with the text translated.
Source: content/i18n/src/<pack>.tsv (English; the `english` pack source is European Portuguese).
Target: content/i18n/<lang>/<pack>.tsv

## Rules
- Keep every key exactly; one line per key; a single TAB between key and text. Never add or drop lines.
- Keep the two-character sequence `\n` exactly where it is (it marks a paragraph or line break), keep `**bold**`
  markers and `• ` bullets, keep numbers, years, units, symbols and formulas as they are (translate only words inside them).
- Keys containing `.viz.` or `.sketch.` are labels drawn inside small diagrams: keep them as short as the source
  (Chinese: about half the number of characters). Use the shortest natural wording.
- `.y` keys in timelines are dates: localise era markers (BCE → a.C. / a. C. / av. J.-C. / 公元前…) but keep them short.
- Quiz options (`.o0`, `.o1`…) stay in the same order. Proper names stay (use the usual local form if one exists:
  Lisbon → Lisboa, London → Londres, Confucius → 孔子).
- Don't convert currencies or units. Keep € amounts.
- Number format follows the target language: pt-PT, pt-BR, es and fr use a decimal comma (0,67 kWh; 3,3 V) and a space or
  point for thousands (2 000 or 2.000; never "2,000"); zh keeps 0.67 and 2,000. Leave version numbers and names alone
  (Web 2.0, GPT-4, Python 3.12).
- Natural, fluent, friendly register for a curious adult — not word-for-word:
  - pt-PT: European Portuguese, informal "tu" (as in the app UI), Portuguese spelling (AO90), e.g. "ecrã", "equipa", "facto".
  - pt-BR: Brazilian Portuguese, "você", Brazilian vocabulary ("tela", "time/equipe", "fato", "trem").
  - es: neutral Spanish from Spain, "tú" (avoid "vosotros" where a neutral form works).
  - fr: standard French, "vous".
  - zh: Simplified Chinese (Mainland conventions), concise, full-width punctuation.
- Accuracy matters more than elegance: never change a fact, number or date.

## How to work (large files)
1. Read the source file in chunks (e.g. 300 lines at a time with the Read tool's offset/limit).
2. Write the translation chunk by chunk: the first chunk with the Write tool, later chunks appended with
   `cat >> content/i18n/<lang>/<pack>.tsv <<'EOF_TSV'` … `EOF_TSV` in Bash (quoted delimiter, so nothing is expanded).
   Saving as you go means no work is lost if you are interrupted. If the target file already exists, continue
   from the first missing key instead of starting again.
3. Check: `python3 tools/i18n.py check <lang> content/i18n/<lang>/<pack>.tsv` → fix every problem until it reports
   0 problems and no untranslated strings.
Only write your own target file(s). Never edit packs/, src files or other translators' files.
