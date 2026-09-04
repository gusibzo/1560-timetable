from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev107.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.107", "Rev.108")

rev108_css = r'''

/* Rev108: keep the remaining quick buttons below the timetable, never over text. */
.side-tools{
  position:relative!important;
  z-index:auto!important;
  top:auto!important;
  right:auto!important;
  bottom:auto!important;
  width:min(460px,calc(100% - 20px))!important;
  margin:12px auto calc(18px + env(safe-area-inset-bottom))!important;
  padding:0 6px!important;
  display:flex!important;
  flex-direction:row!important;
  align-items:center!important;
  justify-content:flex-end!important;
  gap:10px!important;
}
.side-tool{
  width:43px!important;
  height:43px!important;
  flex:0 0 43px!important;
}
#quickCalendar{
  display:none!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev108_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=107",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=108",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev107 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev108-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="108";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
