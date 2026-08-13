from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev49.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.49", "Rev.50")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=49",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=50",{updateViaCache:"none"})',
    1,
)

# Rev50: turn the current departed-trip marker into a small bus and add a
# gentle firefly/twinkle animation, while keeping the elapsed-time badge.
css = r'''
/* Rev50: bus-shaped current-time cursor with firefly glow. */
.grid tbody td.next{
  position:relative!important;
  overflow:visible!important;
  isolation:isolate;
}
body .grid tbody td.next > .time{
  position:relative!important;
  z-index:2!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:72px!important;
  min-width:72px!important;
  height:50px!important;
  min-height:50px!important;
  padding:13px 6px 6px!important;
  border:3px solid #9f7a00!important;
  border-radius:15px 15px 11px 11px!important;
  background:
    linear-gradient(#17853a,#17853a) center 18px / 78% 23px no-repeat,
    linear-gradient(180deg,#ffd94f 0 30%,#f2ad16 30% 100%)!important;
  color:#fff!important;
  font-size:18px!important;
  line-height:1!important;
  font-weight:950!important;
  letter-spacing:-.5px!important;
  text-shadow:0 1px 2px rgba(0,0,0,.45)!important;
  box-shadow:
    0 0 0 2px rgba(255,241,95,.52),
    0 0 9px 4px rgba(218,255,67,.72),
    0 0 20px 8px rgba(111,255,87,.42),
    inset 0 1px 0 rgba(255,255,255,.72)!important;
  transform-origin:center;
  animation:rev50BusFirefly 1.18s ease-in-out infinite alternate!important;
}
body .grid tbody td.next > .time::before{
  content:"";
  position:absolute;
  left:9px;
  right:9px;
  top:5px;
  height:8px;
  border:1px solid rgba(54,73,82,.58);
  border-radius:4px 4px 3px 3px;
  background:linear-gradient(90deg,#eaf8ff 0 46%,#8eaab6 46% 54%,#eaf8ff 54% 100%);
  box-shadow:inset 0 1px 1px rgba(255,255,255,.95);
}
body .grid tbody td.next > .time::after{
  content:"";
  position:absolute;
  left:8px;
  bottom:4px;
  width:7px;
  height:7px;
  border-radius:50%;
  background:#eef6ff;
  box-shadow:
    0 0 0 1px #46515a,
    47px 0 0 #eef6ff,
    47px 0 0 1px #46515a,
    0 0 7px #fff9ad,
    47px 0 7px #fff9ad;
}
.grid tbody td.next::before{
  content:"✦";
  position:absolute;
  z-index:1;
  left:50%;
  top:44%;
  width:1px;
  height:1px;
  color:#fff89a;
  font-size:13px;
  line-height:1;
  pointer-events:none;
  text-shadow:
    -37px -12px 0 #d8ff4d,
    34px -16px 0 #fff6a8,
    -31px 18px 0 #aaff68,
    38px 17px 0 #eaff65,
    -13px -28px 0 #fffbd0,
    17px 30px 0 #d9ff68;
  animation:rev50SparkA .86s ease-in-out infinite alternate;
}
.grid tbody td.next::after{
  content:"•";
  position:absolute;
  z-index:1;
  left:50%;
  top:46%;
  width:1px;
  height:1px;
  color:#eaff57;
  font-size:18px;
  line-height:1;
  pointer-events:none;
  text-shadow:
    -43px 2px 0 #c8ff54,
    42px 1px 0 #fff57b,
    -23px -25px 0 #fff6a1,
    26px 26px 0 #b8ff65;
  animation:rev50SparkB 1.04s ease-in-out infinite alternate-reverse;
}
body .grid tbody td.next > .next-countdown{
  position:relative!important;
  z-index:3!important;
  margin-top:5px!important;
  background:#111827!important;
  color:#fff!important;
  box-shadow:0 2px 5px rgba(0,0,0,.23)!important;
}
@keyframes rev50BusFirefly{
  0%{
    filter:brightness(.96) saturate(.98);
    transform:translateY(0) scale(.985);
    box-shadow:0 0 0 1px rgba(255,241,95,.32),0 0 5px 2px rgba(218,255,67,.44),0 0 11px 4px rgba(111,255,87,.24),inset 0 1px 0 rgba(255,255,255,.68);
  }
  100%{
    filter:brightness(1.12) saturate(1.12);
    transform:translateY(-1px) scale(1.025);
    box-shadow:0 0 0 3px rgba(255,247,130,.68),0 0 13px 6px rgba(226,255,69,.88),0 0 27px 11px rgba(107,255,80,.55),inset 0 1px 0 rgba(255,255,255,.86);
  }
}
@keyframes rev50SparkA{0%{opacity:.25;transform:scale(.7) rotate(-7deg)}100%{opacity:1;transform:scale(1.2) rotate(7deg)}}
@keyframes rev50SparkB{0%{opacity:.18;transform:scale(.65)}100%{opacity:.92;transform:scale(1.15)}}
@media(max-width:380px){
  body .grid tbody td.next > .time{width:66px!important;min-width:66px!important;height:47px!important;min-height:47px!important;font-size:17px!important}
  body .grid tbody td.next > .time::after{box-shadow:0 0 0 1px #46515a,41px 0 0 #eef6ff,41px 0 0 1px #46515a,0 0 7px #fff9ad,41px 0 7px #fff9ad}
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev50-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="50";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
