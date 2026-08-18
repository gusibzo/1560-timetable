from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev63.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.63", "Rev.64")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=63",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=64",{updateViaCache:"none"})',
    1,
)

# Rev64: make the selected bus row unmistakable on a phone screen.
# The full selected timetable row gets the fluorescent yellow-green treatment
# shown in the user's reference screenshot, while the left bus button remains red.
css = r'''
/* Rev64: fluorescent full-row highlight for the selected bus number. */
.grid tbody tr.rev63-row-selected td:not(.no),
.grid tbody tr.rev63-row-selected:nth-child(even) td:not(.no),
body[data-day="sunday"] .grid tbody tr.rev63-row-selected td.edge:not(.no){
  background:#eaff00!important;
  background-image:linear-gradient(180deg,#f3ff34 0%,#eaff00 48%,#dfff00 100%)!important;
  color:#111!important;
  border-top-color:#b7cf00!important;
  box-shadow:
    inset 2px 0 0 rgba(149,174,0,.62),
    inset -2px 0 0 rgba(149,174,0,.62),
    inset 0 2px 0 rgba(192,218,0,.88),
    inset 0 -2px 0 rgba(192,218,0,.88),
    0 0 12px rgba(222,255,0,.30)!important;
  text-shadow:0 1px 0 rgba(255,255,255,.45)!important;
}
.grid tbody tr.rev63-row-selected td:not(.no) .time,
.grid tbody tr.rev63-row-selected td:not(.no) .ext,
.grid tbody tr.rev63-row-selected td:not(.no) .ext b{
  color:#111!important;
}
.grid tbody tr.rev63-row-selected td:not(.no) .ext{
  font-weight:950!important;
  text-shadow:none!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev64-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="64";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
