from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev104.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.104", "Rev.105")

old_route = '<div class="route-no">1560<small id="season-label">여름</small></div>'
new_route = '<div class="route-no"><span class="rev105-ruby">1560</span><small id="season-label">여름</small></div>'
if text.count(old_route) != 1:
    raise RuntimeError("Rev104 route number was not found exactly once")
text = text.replace(old_route, new_route, 1)

rev105_css = r'''

/* Rev105: deep ruby foil with small reflective flecks, without pink glow. */
.route-no{
  color:#a40028!important;
  text-shadow:none!important;
}
.route-no .rev105-ruby{
  display:inline-block;
  color:#a40028!important;
  background:
    radial-gradient(circle,#ffd09a 0 1.3px,#ff6a42 1.5px,transparent 2.4px) 1px 1px/17px 16px,
    radial-gradient(circle,#ff8a55 0 1.5px,#d71336 1.8px,transparent 2.7px) 9px 8px/19px 18px,
    linear-gradient(180deg,#d31942 0%,#ad002c 46%,#780020 100%);
  -webkit-background-clip:text;
  background-clip:text;
  -webkit-text-fill-color:transparent;
  text-shadow:none!important;
  filter:drop-shadow(0 2px 1px rgba(54,0,15,.58));
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
text = text.replace("</style>", rev105_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=104",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=105",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev104 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev105-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="105";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
