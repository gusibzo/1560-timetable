from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev105.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.105", "Rev.106")

old_route = '<div class="route-no"><span class="rev105-ruby">1560</span><small id="season-label">여름</small></div>'
new_route = '<div class="route-no">1560<small id="season-label">여름</small></div>'
if text.count(old_route) != 1:
    raise RuntimeError("Rev105 ruby route number was not found exactly once")
text = text.replace(old_route, new_route, 1)

rev106_css = r'''

/* Rev106: restore the brighter dimensional red preferred in Rev104. */
.route-no{
  color:#e60036!important;
  -webkit-text-fill-color:#e60036!important;
  text-shadow:0 1px 0 #ff879f,0 0 8px rgba(255,0,58,.42),0 2px 2px rgba(92,0,22,.34)!important;
  filter:none!important;
}
.route-no small{
  color:#ffd46b!important;
  -webkit-text-fill-color:#ffd46b!important;
  text-shadow:none!important;
  filter:none!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev106_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=105",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=106",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev105 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev106-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="106";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
