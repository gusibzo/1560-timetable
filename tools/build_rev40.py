from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev39.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.39", "Rev.40")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=39",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=40",{updateViaCache:"none"})',
    1,
)

css = r'''
/* Rev40: only the headers to the right of '순번' use light pink.
   Restore the sequence-number cells below to their original appearance. */
.grid thead th:first-child{
  background:#c2185b!important;
  color:#fff!important;
  border-color:#a3154d!important;
  text-shadow:0 1px 1px rgba(0,0,0,.22)!important;
}
.grid thead th:not(:first-child){
  background:#f8bbd0!important;
  color:#8a1546!important;
  border-color:#eca0bd!important;
  text-shadow:none!important;
}
.grid tbody td.no,
.grid tr:nth-child(even) td.no{
  background:linear-gradient(90deg,var(--accent-soft),transparent)!important;
  color:var(--accent)!important;
  border-color:var(--line)!important;
  font-weight:900!important;
  text-shadow:none!important;
  box-shadow:none!important;
}
.grid tr.row-highlight td.no,
body[data-day="sunday"] .grid tr.row-highlight td.no{
  background:#dfff00!important;
  color:#111!important;
  border-color:#c8db00!important;
  text-shadow:none!important;
  box-shadow:inset 0 0 0 1px rgba(135,150,0,.42)!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev40-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="40";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
