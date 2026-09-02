from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev102.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.102", "Rev.103")

rev103_css = r'''

/* Rev103: light-red sequence header and light-blue 1560A/B shortcuts. */
.grid thead th:first-child{
  background:linear-gradient(180deg,#ffcaca,#ffaaaa)!important;
  color:#7d1f1f!important;
  border-color:#ef8e8e!important;
  text-shadow:none!important;
}
.info-bar #rev79-gyeonggi-card #rev101-route-a,
.info-bar #rev79-gyeonggi-card #rev101-route-b{
  border-color:#79b8e8!important;
  background:linear-gradient(180deg,#dff2ff,#acd8f7)!important;
  color:#124f7e!important;
  box-shadow:0 3px 0 #5591bd,0 4px 8px rgba(61,125,174,.24)!important;
}
.info-bar #rev79-gyeonggi-card #rev101-route-a:active,
.info-bar #rev79-gyeonggi-card #rev101-route-b:active{
  background:linear-gradient(180deg,#cceaff,#95c9ee)!important;
  box-shadow:0 1px 0 #5591bd,0 2px 5px rgba(61,125,174,.22)!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev103_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=102",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=103",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev102 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev103-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="103";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
