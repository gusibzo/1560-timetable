from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev116.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.116", "Rev.117")

rev117_css = r'''

/* Rev117: lift the two lower circular tools and remove the old two-line spacer. */
.wrap{
  padding-bottom:0!important;
}
.side-tools{
  margin:4px auto 0!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev117_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=116",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=117",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev116 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev117-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="117";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
