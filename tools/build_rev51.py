from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev50.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.50", "Rev.51")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=50",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=51",{updateViaCache:"none"})',
    1,
)

# Rev51: make the glowing current-trip cursor resemble the user's real
# red/silver 1560 hydrogen bus photo more closely while keeping the firefly
# animation and elapsed-time badge from Rev50.
css = r'''
/* Rev51: real 1560 red/silver hydrogen-bus inspired current cursor. */
body .grid tbody td.next > .time{
  width:82px!important;
  min-width:82px!important;
  height:62px!important;
  min-height:62px!important;
  padding:22px 4px 8px!important;
  border:3px solid #5f2a22!important;
  border-radius:17px 17px 10px 10px!important;
  color:#fff!important;
  font-size:18px!important;
  line-height:1!important;
  font-weight:950!important;
  letter-spacing:-.6px!important;
  text-shadow:0 2px 3px rgba(0,0,0,.75)!important;
  background:
    radial-gradient(circle at 16% 82%,#f7fbff 0 4px,#333c45 4.5px 6px,transparent 6.5px),
    radial-gradient(circle at 84% 82%,#f7fbff 0 4px,#333c45 4.5px 6px,transparent 6.5px),
    linear-gradient(180deg,
      #ee3b37 0 18%,
      #151a20 18% 61%,
      #de302e 61% 72%,
      #c9cdd1 72% 91%,
      #24282d 91% 100%)!important;
  box-shadow:
    0 0 0 2px rgba(255,242,97,.58),
    0 0 10px 4px rgba(218,255,67,.80),
    0 0 23px 10px rgba(111,255,87,.47),
    inset 0 1px 0 rgba(255,255,255,.72)!important;
}
body .grid tbody td.next > .time::before{
  content:"1560A"!important;
  left:16px!important;
  right:16px!important;
  top:7px!important;
  height:10px!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  border:1px solid rgba(91,104,111,.62)!important;
  border-radius:2px!important;
  background:#11161b!important;
  color:#ff4b42!important;
  font:900 7px/1 ui-monospace,SFMono-Regular,Menlo,monospace!important;
  letter-spacing:.7px!important;
  text-shadow:0 0 3px rgba(255,75,66,.85)!important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.04)!important;
}
body .grid tbody td.next > .time::after{
  content:""!important;
  position:absolute!important;
  z-index:4!important;
  top:18px!important;
  left:-8px!important;
  width:7px!important;
  height:19px!important;
  border-radius:5px 2px 2px 5px!important;
  background:#22272c!important;
  box-shadow:83px 0 0 #22272c!important;
  pointer-events:none!important;
}
body .grid tbody td.next > .next-countdown{
  margin-top:6px!important;
  border-radius:999px!important;
  padding:3px 7px!important;
  font-size:9px!important;
  letter-spacing:-.15px!important;
}
.grid tbody td.next::before{
  text-shadow:
    -42px -11px 0 #d8ff4d,
    39px -17px 0 #fff6a8,
    -36px 20px 0 #aaff68,
    42px 19px 0 #eaff65,
    -14px -34px 0 #fffbd0,
    19px 35px 0 #d9ff68!important;
}
.grid tbody td.next::after{
  text-shadow:
    -47px 3px 0 #c8ff54,
    46px 2px 0 #fff57b,
    -27px -29px 0 #fff6a1,
    29px 31px 0 #b8ff65!important;
}
@media(max-width:380px){
  body .grid tbody td.next > .time{
    width:76px!important;min-width:76px!important;
    height:58px!important;min-height:58px!important;
    padding-top:21px!important;font-size:17px!important;
  }
  body .grid tbody td.next > .time::after{box-shadow:77px 0 0 #22272c!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev51-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="51";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
