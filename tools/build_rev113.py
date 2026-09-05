from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev112.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.112", "Rev.113")

rev113_css = r'''

/* Rev113: keep the portrait layout full width without breaking the sticky header. */
html{
  width:100%!important;
  min-width:0!important;
  overflow-x:hidden!important;
  overflow-y:visible!important;
}
body{
  display:block!important;
  width:100%!important;
  min-width:0!important;
  max-width:none!important;
  overflow:visible!important;
}
.wrap{
  display:block!important;
  width:100%!important;
  min-width:0!important;
  max-width:none!important;
  margin:0!important;
  overflow-x:visible!important;
  overflow-y:visible!important;
}
.sticky-head{
  position:-webkit-sticky!important;
  position:sticky!important;
  top:env(safe-area-inset-top,0px)!important;
  z-index:8800!important;
  isolation:isolate!important;
  background:var(--bg)!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev113_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=112",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=113",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev112 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev113-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="113";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
