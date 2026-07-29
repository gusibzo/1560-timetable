from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev37.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.37", "Rev.38")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=37",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=38",{updateViaCache:"none"})',
    1,
)

css = r'''
/* Rev38: switch-style outlines for weather, Gyeonggi Bus and road traffic buttons. */
.info-bar{gap:10px!important;padding:10px!important}
.info-bar>a,.info-bar>button{
  box-sizing:border-box!important;
  min-width:0!important;
  min-height:54px!important;
  border:2px solid #8e99a7!important;
  border-radius:20px!important;
  background:linear-gradient(180deg,#ffffff 0%,#eef2f6 100%)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.95),inset 0 -1px 0 rgba(91,105,121,.18),0 3px 7px rgba(30,45,60,.18)!important;
  color:#171b20!important;
  font-family:inherit!important;
  font-weight:900!important;
  cursor:pointer!important;
  -webkit-tap-highlight-color:transparent;
  transition:transform .08s ease,box-shadow .08s ease,background .08s ease;
}
.info-bar>a:active,.info-bar>button:active{
  transform:translateY(1px);
  background:linear-gradient(180deg,#e5eaf0 0%,#f8fafc 100%)!important;
  box-shadow:inset 0 2px 5px rgba(40,55,70,.22),0 1px 3px rgba(30,45,60,.12)!important;
}
@media(max-width:380px){
  .info-bar{gap:7px!important;padding:8px!important}
  .info-bar>a,.info-bar>button{min-height:50px!important;border-radius:17px!important;font-size:13px!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev38-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="38";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
