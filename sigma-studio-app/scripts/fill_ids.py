"""Fill @@NAME@@ placeholders in programs/<name>.tpl from ids.json (+ ids_static.json).

    python3 fill_ids.py B C        # writes programs/B.py, programs/C.py and lists anything unfilled
Run from the build directory. Add the NAME|id lines each call prints to ids.json first
(studio_kit.collect_ids does that from a pasted result).
"""
import json, os, re, sys

ids = {}
for f in ("ids.json", "ids_static.json"):
    if os.path.exists(f):
        ids.update(json.load(open(f)))
for name in sys.argv[1:]:
    s = open(f"programs/{name}.tpl").read()
    for k, v in ids.items():
        s = s.replace("@@" + k + "@@", v)
    left = sorted(set(re.findall(r"@@\w+@@", s)))
    open(f"programs/{name}.py", "w").write(s)
    print(name, "unfilled:", left or "none")
