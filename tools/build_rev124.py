from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev123.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.123", "Rev.124")

anchor = 'let DATA=rev91Season==="autumn"?AUTUMN_DATA:SUMMER_DATA;'
special_schedule = r'''

/* Rev124: temporary five-bus timetable for the four-day 2026 Chuseok holiday. */
const REV124_FIVE_BUS_DATES=new Set([
 "2026-09-24","2026-09-25","2026-09-26","2026-09-27"
]);
const REV124_FIVE_BUS_DATA={
 label:"추석 연휴(5대)",count:5,accent:"#e23b2e",rows:[
  {no:1,t:["5:00","8:20","12:00","16:00","19:20"]},
  {no:2,t:["5:40","9:10","12:50","16:40","20:00"]},
  {no:3,t:["6:20","10:00","13:40","17:20","20:50"]},
  {no:4,t:["7:00","10:50","14:30","18:00","21:40"]},
  {no:5,t:["7:40","11:30","15:20","18:40","22:30"]}
 ]
};
const rev124TodayIsFiveBus=REV124_FIVE_BUS_DATES.has(dateKey(new Date()));
if(rev124TodayIsFiveBus){
 DATA={...DATA,sunday:REV124_FIVE_BUS_DATA};
 const sundayCount=document.querySelector('.seg[data-day="sunday"] .cnt');
 if(sundayCount)sundayCount.textContent="5대";
}
'''
if text.count(anchor) != 1:
    raise RuntimeError("Rev123 timetable data anchor is missing or duplicated")
text = text.replace(anchor, anchor + special_schedule, 1)

registration = 'navigator.serviceWorker.register("./sw.js?v=123",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev123 service worker registration is missing")
text = text.replace(registration, registration.replace("v=123", "v=124"), 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev124-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="124";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
