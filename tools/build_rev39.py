from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev38.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.38", "Rev.39")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=38",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=39",{updateViaCache:"none"})',
    1,
)

css = r'''
/* Rev39: deep-pink background for the sequence-number column. */
.grid thead th:first-child{
  background:#c2185b!important;
  color:#fff!important;
  border-color:#a3154d!important;
  text-shadow:0 1px 1px rgba(0,0,0,.22);
}
.grid tbody td.no{
  background:#d81b60!important;
  color:#fff!important;
  border-color:#b81651!important;
  font-weight:950!important;
  text-shadow:0 1px 1px rgba(0,0,0,.22);
  box-shadow:inset -1px 0 0 rgba(255,255,255,.22)!important;
}
.grid tr.row-highlight td.no,
body[data-day="sunday"] .grid tr.row-highlight td.no{
  background:#d81b60!important;
  color:#fff!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev39-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="39";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
