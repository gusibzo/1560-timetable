from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev74.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.74", "Rev.75")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=74",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=75",{updateViaCache:"none"})',
    1,
)

# Rev75: enlarge both side panels while keeping the center counter dominant.
# Preserve Rev74's single-row current | counter | next layout.
css = r'''
/* Rev75: larger left/right briefing text for quick readability. */
.rev74-current-card .rev57-briefing-k,
.rev74-next-card .rev57-briefing-k{
  font-size:11px!important;
  font-weight:950!important;
  line-height:1.1!important;
}
#rev57-current{
  font-size:14px!important;
  font-weight:950!important;
  letter-spacing:-.35px!important;
}
#rev57-next{
  font-size:13.5px!important;
  font-weight:950!important;
  letter-spacing:-.45px!important;
}
@media(max-width:380px){
  .rev74-current-card .rev57-briefing-k,
  .rev74-next-card .rev57-briefing-k{
    font-size:10.5px!important;
  }
  #rev57-current{font-size:12.5px!important}
  #rev57-next{font-size:12.2px!important;letter-spacing:-.55px!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev75-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="75";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
