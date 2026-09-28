from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base = Path(__file__).with_name("build_rev135.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old

index = root / "index.html"
text = index.read_text(encoding="utf-8")
line = "border-right:1px solid var(--row-dot)!important;"
assert text.count(line) == 1, "Rev135 vertical line is missing"
text = text.replace(line, line + "\n  border-left:1px solid var(--row-dot)!important;", 1)
text = text.replace("Rev.135", "Rev.136").replace("./sw.js?v=135", "./sw.js?v=136")
index.write_text(text, encoding="utf-8")
sw = root / "sw.js"
text = sw.read_text(encoding="utf-8").replace("1560-timetable-rev135-v1", "1560-timetable-rev136-v1").replace('REVISION="135"', 'REVISION="136"')
sw.write_text(text, encoding="utf-8")
