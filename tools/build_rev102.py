from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev101.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.101", "Rev.102")

rev102_css = r'''

/* Rev102: purple work calendar and yellow 1560A shortcut. */
.clock #rev58-today-work.rev88-clock-calendar,
.clock #rev58-today-work.rev88-clock-calendar.checked{
  border-color:#c79cff!important;
  background:linear-gradient(180deg,#8b5cf6,#6d28d9)!important;
  color:#fff!important;
  box-shadow:0 3px 0 #4c1d95,0 5px 12px rgba(76,29,149,.30),inset 0 1px 0 rgba(255,255,255,.30)!important;
}
.clock #rev58-today-work.rev88-clock-calendar:active{
  transform:translateY(2px)!important;
  background:linear-gradient(180deg,#7c3aed,#5b21b6)!important;
  box-shadow:0 1px 0 #4c1d95,0 2px 6px rgba(76,29,149,.26)!important;
}
.info-bar #rev101-route-a{
  border-color:#ffbf00!important;
  background:linear-gradient(180deg,#ffe66a,#ffd43b)!important;
  color:#111!important;
  box-shadow:0 3px 0 #b77900,0 4px 8px rgba(183,121,0,.28)!important;
}
.info-bar #rev79-gyeonggi-card #rev101-route-a:active{
  background:linear-gradient(180deg,#ffd84a,#f6c500)!important;
  box-shadow:0 1px 0 #b77900,0 2px 5px rgba(183,121,0,.24)!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev102_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=101",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=102",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev101 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev102-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="102";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
