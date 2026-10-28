#!/bin/bash
# finish.sh <lang> <pack...> : localise numbers, build the language pack, report card-diagram problems
cd "$(dirname "$0")/.." || exit 1
L=$1; shift
for p in "$@"; do
  for f in content/i18n/$L/$p*.tsv; do [ "$L" != zh ] && python3 tools/numfmt.py $L $f | grep -v ' 0 lines'; done
  python3 tools/i18n.py apply $L $p | tail -1
  [ -f packs/$L/$p.json ] && timeout 300 python3 tools/check_viz.py $L/$p | grep -E '#card'
done
true
