from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev120.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.120", "Rev.121")
css = """
/* Rev121: fluorescent lime for the selected timetable row. */
.rev63-row-btn[aria-pressed="true"] {
  background:#eaff00;color:#111;border-color:#a8bd00;
  box-shadow:0 0 0 2px #d8e889;
}
.grid tbody tr.rev63-row-selected td:not(.no),
.grid tbody tr.rev63-row-selected:nth-child(even) td:not(.no),
body[data-day="sunday"] .grid tbody tr.rev63-row-selected td.edge:not(.no) {
  background:#eaff00!important;background-image:none!important;
  color:#111!important;border-top-color:#a8bd00!important;
  box-shadow:inset 0 2px 0 #a8bd00,inset 0 -2px 0 #a8bd00!important;
  text-shadow:none!important;
}
"""
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", "\n" + css + "\n</style>", 1)
registration = 'navigator.serviceWorker.register("./sw.js?v=120",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev120 service worker registration is missing")
text = text.replace(registration, registration.replace("v=120", "v=121"), 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev121-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="121";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
