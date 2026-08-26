from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev82.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.82", "Rev.83")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=82",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=83",{updateViaCache:"none"})',
    1,
)

css = r'''
/* Rev83: restore the fixed top controls while the timetable scrolls below. */
html{
  overflow-x:hidden!important;
  overflow-y:visible!important;
}
body{
  overflow:visible!important;
}
.wrap{
  overflow-x:visible!important;
  overflow-y:visible!important;
}
.sticky-head{
  position:-webkit-sticky!important;
  position:sticky!important;
  top:env(safe-area-inset-top,0px)!important;
  z-index:8800!important;
  isolation:isolate!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev83-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="83";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
