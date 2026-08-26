from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev80.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.80", "Rev.81")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=80",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=81",{updateViaCache:"none"})',
    1,
)

# Rev81: the left current-departure card shows only the scheduled time.
# Removing the bus/trip labels prevents the important time from being clipped.
old_current = '''currentEl.textContent=current.kind==="ext"
        ? `${current.ri+1}번 · 추가 ${current.time}`
        : `${current.ri+1}번 · ${current.ci+1}회 ${current.time}`;'''
new_current = '''currentEl.textContent=current.time;'''
if text.count(old_current) != 1:
    raise RuntimeError("Rev80 current-departure text was not found exactly once")
text = text.replace(old_current, new_current, 1)

css = r'''
/* Rev81: keep the current departure time large, centered, and fully visible. */
.rev74-current-card{
  align-items:center!important;
  text-align:center!important;
}
#rev57-current{
  width:100%!important;
  font-size:20px!important;
  line-height:1.1!important;
  letter-spacing:-.4px!important;
  overflow:visible!important;
  text-overflow:clip!important;
  text-align:center!important;
}
@media(max-width:380px){
  #rev57-current{font-size:18px!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev81-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="81";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
