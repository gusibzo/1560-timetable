from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev96.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.96", "Rev.97")

rev97_css = r'''

/* Rev97: weather and road-traffic buttons match the coworker-family blue. */
.info-bar > a[href*="weather.go.kr"],
.info-bar > #roadTrafficBtn{
  background:#2b66b1!important;
  color:#fff!important;
  border-color:#1e4f8f!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.15),0 3px 0 #194374,0 4px 9px rgba(29,72,126,.25)!important;
}
.info-bar > a[href*="weather.go.kr"]:active,
.info-bar > #roadTrafficBtn:active{
  background:#235896!important;
  color:#fff!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 1px 0 #194374,0 2px 5px rgba(29,72,126,.22)!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev97_css + "</style>", 1)

text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=96",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=97",{updateViaCache:"none"})',
    1,
)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev97-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="97";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
