from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev26.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.26", "Rev.27")

# Correct the first and second weekday intervals from 2h30m to 2h25m.
old_cell = '<div class="gap-weekday">2시간30분</div>'
new_cell = '<div class="gap-weekday">2시간25분</div>'
if text.count(old_cell) < 2:
    raise RuntimeError("the two weekday 2시간30분 cells were not found")
text = text.replace(old_cell, new_cell, 2)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev27-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
