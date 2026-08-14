from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev51.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.51", "Rev.52")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=51",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=52",{updateViaCache:"none"})',
    1,
)

# Rev52: make the real-bus cursor more compact and nudge it left so the next
# timetable column remains readable, while making the firefly glow larger.
css = r'''
/* Rev52: smaller left-shifted bus cursor, larger firefly halo. */
body .grid tbody td.next > .time{
  width:70px!important;
  min-width:70px!important;
  height:54px!important;
  min-height:54px!important;
  padding:19px 3px 7px!important;
  left:-7px!important;
  border-width:2.5px!important;
  border-radius:15px 15px 9px 9px!important;
  font-size:16.5px!important;
  box-shadow:
    0 0 0 3px rgba(255,244,103,.62),
    0 0 16px 8px rgba(224,255,72,.86),
    0 0 34px 17px rgba(118,255,87,.52),
    inset 0 1px 0 rgba(255,255,255,.76)!important;
  animation:rev52BusFirefly 1.08s ease-in-out infinite alternate!important;
}
body .grid tbody td.next > .time::before{
  left:13px!important;
  right:13px!important;
  top:6px!important;
  height:9px!important;
  font-size:6.5px!important;
}
body .grid tbody td.next > .time::after{
  top:16px!important;
  left:-6px!important;
  width:6px!important;
  height:17px!important;
  box-shadow:70px 0 0 #22272c!important;
}
body .grid tbody td.next > .next-countdown{
  left:-7px!important;
  margin-top:5px!important;
  padding:3px 6px!important;
  font-size:8.5px!important;
}
.grid tbody td.next::before{
  left:46%!important;
  top:43%!important;
  font-size:18px!important;
  text-shadow:
    -54px -16px 0 #d8ff4d,
    52px -22px 0 #fff6a8,
    -48px 27px 0 #aaff68,
    55px 26px 0 #eaff65,
    -20px -43px 0 #fffbd0,
    25px 45px 0 #d9ff68,
    -61px 7px 0 #c9ff52,
    62px 4px 0 #fff184!important;
  animation:rev52SparkA .76s ease-in-out infinite alternate!important;
}
.grid tbody td.next::after{
  left:46%!important;
  top:45%!important;
  font-size:23px!important;
  text-shadow:
    -60px 4px 0 #c8ff54,
    59px 3px 0 #fff57b,
    -36px -37px 0 #fff6a1,
    39px 40px 0 #b8ff65,
    -55px 35px 0 #e8ff63,
    56px -35px 0 #d9ff6e!important;
  animation:rev52SparkB .92s ease-in-out infinite alternate-reverse!important;
}
@keyframes rev52BusFirefly{
  0%{
    filter:brightness(.98) saturate(1.02);
    transform:translateY(0) scale(.99);
    box-shadow:0 0 0 2px rgba(255,244,103,.45),0 0 11px 5px rgba(224,255,72,.58),0 0 26px 13px rgba(118,255,87,.34),inset 0 1px 0 rgba(255,255,255,.70);
  }
  100%{
    filter:brightness(1.13) saturate(1.14);
    transform:translateY(-1px) scale(1.025);
    box-shadow:0 0 0 4px rgba(255,248,140,.78),0 0 21px 10px rgba(230,255,77,.96),0 0 44px 22px rgba(112,255,80,.60),inset 0 1px 0 rgba(255,255,255,.88);
  }
}
@keyframes rev52SparkA{0%{opacity:.22;transform:scale(.72) rotate(-8deg)}100%{opacity:1;transform:scale(1.32) rotate(8deg)}}
@keyframes rev52SparkB{0%{opacity:.16;transform:scale(.68)}100%{opacity:.96;transform:scale(1.28)}}
@media(max-width:380px){
  body .grid tbody td.next > .time{
    width:66px!important;min-width:66px!important;
    height:51px!important;min-height:51px!important;
    padding-top:18px!important;
    left:-6px!important;
    font-size:15.5px!important;
  }
  body .grid tbody td.next > .time::after{box-shadow:66px 0 0 #22272c!important}
  body .grid tbody td.next > .next-countdown{left:-6px!important;font-size:8px!important}
}
@media(prefers-reduced-motion:reduce){
  body .grid tbody td.next > .time,.grid tbody td.next::before,.grid tbody td.next::after{animation:none!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev52-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="52";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
