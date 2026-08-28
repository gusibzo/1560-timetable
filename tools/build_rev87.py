from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev86.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.86", "Rev.87")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=86",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=87",{updateViaCache:"none"})',
    1,
)

rev87_css = '''

/* Rev87: larger header date and high-contrast yellow live clock. */
#hdr-date{
  display:inline-block!important;
  margin-top:4px!important;
  color:#fff!important;
  font-size:18px!important;
  font-weight:950!important;
  line-height:1.1!important;
  letter-spacing:.35px!important;
  white-space:nowrap!important;
}
.clock{
  margin-top:10px!important;
  padding:10px 12px!important;
  border-top:0!important;
  border-radius:12px!important;
  background:#ffd83d!important;
  color:#111!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 2px 0 rgba(0,0,0,.25)!important;
}
.clock .live{
  color:#111!important;
  font-size:13px!important;
  font-weight:950!important;
}
.clock .dot{
  background:#111!important;
  box-shadow:none!important;
}
#now{
  color:#111!important;
  font-size:clamp(20px,6.2vw,27px)!important;
  font-weight:950!important;
  line-height:1!important;
  letter-spacing:.7px!important;
}
@media(max-width:380px){
  #hdr-date{font-size:17px!important}
  .clock{padding:9px 10px!important}
  .clock .live{font-size:12px!important}
  #now{font-size:clamp(19px,6vw,24px)!important}
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev87_css + "</style>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev87-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="87";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
