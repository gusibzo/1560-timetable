from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev114.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.114", "Rev.115")

two_bottom_rows = '''    <div class="gap-weekday-label">주간(평일)</div>
    <div class="gap-weekday">2시간25분</div>
    <div class="gap-weekday">2시간25분</div>
    <div class="gap-weekday">2시간35분</div>
    <div class="gap-weekday">2시간25분</div>

    <div class="gap-weekend-label">주말.공휴일</div>
    <div class="gap-weekend">2시간25분</div>
    <div class="gap-weekend">2시간25분</div>
    <div class="gap-weekend">2시간25분</div>
    <div class="gap-weekend">2시간25분</div>
'''
if two_bottom_rows not in text:
    raise RuntimeError("The two bottom horizontal rows were not found")
text = text.replace(two_bottom_rows, "", 1)

rev115_css = r'''

/* Rev115: the two lower horizontal guide rows were removed. */
.rev24-gap-grid>.gap-station,
.rev24-gap-grid>.black:nth-child(n+7):nth-child(-n+10){border-bottom:0!important}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev115_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=114",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=115",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev114 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev115-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="115";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
