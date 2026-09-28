from pathlib import Path
import runpy
import sys
root = Path(sys.argv[1] if len(sys.argv)>1 else "_site")
base = Path(__file__).with_name("build_rev136.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old
index = root / "index.html"
text = index.read_text(encoding="utf-8")
needle = "border-right:1px solid var(--row-dot)!important;\n  border-left:1px solid var(--row-dot)!important;"
assert text.count(needle)==1
text = text.replace(needle, "box-shadow:inset 1px 0 0 var(--row-dot),inset -1px 0 0 var(--row-dot)!important;", 1)
text = text.replace("Rev.136","Rev.137").replace("./sw.js?v=136","./sw.js?v=137")
index.write_text(text,encoding="utf-8")
sw = root / "sw.js"
text = sw.read_text(encoding="utf-8").replace("1560-timetable-rev136-v1","1560-timetable-rev137-v1").replace('REVISION="136"','REVISION="137"')
sw.write_text(text,encoding="utf-8")
