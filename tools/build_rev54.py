from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev53.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.53", "Rev.54")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=53",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=54",{updateViaCache:"none"})',
    1,
)

# Rev54: public holidays (including substitute holidays produced by the
# existing calendar holiday engine) automatically use the Sunday/holiday
# timetable instead of the weekday timetable.
old_today = 'const todayKey=()=>{const d=new Date().getDay();return d===0?"sunday":d===6?"saturday":"weekday"};'
new_today = '''const todayKey=()=>{\n const now=new Date();\n const info=calendarInfo(now);\n if(info&&info.holidays&&info.holidays.length)return "sunday";\n const d=now.getDay();\n return d===0?"sunday":d===6?"saturday":"weekday";\n};'''
if old_today not in text:
    raise RuntimeError("todayKey definition not found")
text = text.replace(old_today, new_today, 1)

old_label = 'document.getElementById("today-label").textContent=`오늘 · ${["일","월","화","수","목","금","토"][n.getDay()]}요일`;'
new_label = '''const rev54Info=calendarInfo(n);\n const rev54Holiday=(rev54Info&&rev54Info.holidays&&rev54Info.holidays.length)?` · ${rev54Info.holidays[0]}`:"";\n document.getElementById("today-label").textContent=`오늘 · ${["일","월","화","수","목","금","토"][n.getDay()]}요일${rev54Holiday}`;'''
if old_label in text:
    text = text.replace(old_label, new_label, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev54-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="54";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
