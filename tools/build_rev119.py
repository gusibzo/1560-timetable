from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev118.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.118", "Rev.119")

rev119_css = r'''

/* Rev119: morning yellow / afternoon deep navy. */
.calendar-day.rev58-work-day.rev118-work-am{
  background:#ffd84d!important;
  color:#161616!important;
  box-shadow:inset 0 0 0 2px #d9a900,0 1px 0 #dfe3e8!important;
}
.calendar-day.rev58-work-day.rev118-work-am.selected{
  background:#ffca28!important;
  box-shadow:inset 0 0 0 2px #9b7300,0 0 0 2px rgba(217,169,0,.24)!important;
}
.calendar-day.rev118-work-am .solar-no,
.calendar-day.rev118-work-am .lunar,
.calendar-day.rev118-work-am .holiday-name,
.calendar-day.rev118-work-am .event-name{
  color:#161616!important;
}
.calendar-day.rev118-work-am::after{
  background:#f3b800!important;
  color:#111!important;
}
.calendar-day.rev58-work-day.rev118-work-pm{
  background:#102a4c!important;
  color:#fff!important;
  box-shadow:inset 0 0 0 2px #06172e,0 1px 0 #dfe3e8!important;
}
.calendar-day.rev58-work-day.rev118-work-pm.selected{
  background:#071b34!important;
  box-shadow:inset 0 0 0 2px #fff,0 0 0 2px rgba(7,27,52,.30)!important;
}
.calendar-day.rev118-work-pm .solar-no,
.calendar-day.rev118-work-pm .lunar,
.calendar-day.rev118-work-pm .holiday-name,
.calendar-day.rev118-work-pm .event-name{
  color:#fff!important;
}
.calendar-day.rev118-work-pm::after{
  background:#061528!important;
  color:#fff!important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.42);
}
.rev118-legend-am{
  background:#ffd84d!important;
  color:#111!important;
  box-shadow:inset 0 0 0 1px #d9a900;
}
.rev118-legend-pm{
  background:#102a4c!important;
  color:#fff!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev119_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=118",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=119",{updateViaCache:"none"})'
if text.count(old_registration) != 1:
    raise RuntimeError("Rev118 service worker registration was not found exactly once")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev119-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="119";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
