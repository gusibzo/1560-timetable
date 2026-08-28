from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev88.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.88", "Rev.89")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=88",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=89",{updateViaCache:"none"})',
    1,
)

# Rev89: show the weekday next to the large header date while keeping the
# smaller status-line date unchanged.
old_date_line = ' document.getElementById("hdr-date").textContent=date;document.getElementById("status-date").textContent=date;'
new_date_line = ''' const weekday=`${["일","월","화","수","목","금","토"][n.getDay()]}요일`;
 document.getElementById("hdr-date").textContent=`${date} · ${weekday}`;
 document.getElementById("status-date").textContent=date;'''
if text.count(old_date_line) != 1:
    raise RuntimeError("Rev88 header date assignment was not found exactly once")
text = text.replace(old_date_line, new_date_line, 1)

rev89_css = '''

/* Rev89: keep the date and weekday large but on one mobile-friendly line. */
#hdr-date{
  font-size:clamp(15px,4.2vw,18px)!important;
  letter-spacing:0!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev89_css + "</style>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev89-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="89";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
