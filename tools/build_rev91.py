from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev90.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.90", "Rev.91")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=90",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=91",{updateViaCache:"none"})',
    1,
)
text = text.replace(
    "<title>1560 여름 시간표 앱 · Rev.91</title>",
    "<title>1560 계절 시간표 앱 · Rev.91</title>",
    1,
)

# Keep the visible season and inspection details addressable at the date boundary.
old_route = '<div class="route-no">1560<small>여름</small></div>'
new_route = '<div class="route-no">1560<small id="season-label">여름</small></div>'
if text.count(old_route) != 1:
    raise RuntimeError("Rev90 route season label was not found exactly once")
text = text.replace(old_route, new_route, 1)

old_notice = '<div class="notice"><span>검차일</span><b>매주 월요일</b></div>'
new_notice = '<div class="notice"><span>검차일</span><b id="inspection-days">매주 월요일</b></div>'
if text.count(old_notice) != 1:
    raise RuntimeError("Rev90 inspection notice was not found exactly once")
text = text.replace(old_notice, new_notice, 1)

# Preserve the existing summer timetable, then add the September autumn timetable
# from 시간표2026.09claude.xlsx as a separate data set.
if text.count("const DATA={") != 1:
    raise RuntimeError("Rev90 timetable data declaration was not found exactly once")
text = text.replace("const DATA={", "const SUMMER_DATA={", 1)

autumn_data = r'''
const AUTUMN_DATA={
 weekday:{label:"평일",count:13,accent:"#177226",rows:[
  {no:1,t:["5:00","8:00","11:50","15:30","19:20"]},
  {no:2,t:["5:15","8:20","12:10","15:50","19:40"]},
  {no:3,t:["5:30","8:40","12:30","16:10","20:00"]},
  {no:4,t:["5:45","9:00","12:50","16:30","20:15"]},
  {no:5,t:["6:00","9:20","13:10","16:45","20:30"]},
  {no:6,t:["6:20","9:40","13:30","17:00","20:45"]},
  {no:7,t:["6:25","10:00","13:45","17:15","21:00"]},
  {no:8,t:["6:30","10:15","14:00","17:30","21:15"]},
  {no:9,t:["6:40","10:30","14:15","17:45","21:30"]},
  {no:10,t:["6:50","10:45","14:30","18:00","21:45"]},
  {no:11,t:["7:00","11:00","14:45","18:20","22:00"],ext:"23:10"},
  {no:12,t:["7:20","11:15","15:00","18:40","22:15"],ext:"23:30"},
  {no:13,t:["7:40","11:30","15:15","19:00","22:30"],ext:"23:50"}
 ],charter:true},
 saturday:{label:"토요일",count:9,accent:"#1e63d6",rows:[
  {no:1,t:["5:00","8:00","11:50","15:40","19:10"]},
  {no:2,t:["5:20","8:25","12:20","16:00","19:30"]},
  {no:3,t:["5:40","8:50","12:45","16:20","19:50"]},
  {no:4,t:["6:00","9:15","13:10","16:40","20:15"]},
  {no:5,t:["6:20","9:40","13:35","17:05","20:40"]},
  {no:6,t:["6:40","10:05","14:00","17:30","21:05"]},
  {no:7,t:["7:00","10:30","14:25","17:55","21:30"],ext:"22:50"},
  {no:8,t:["7:20","10:55","14:50","18:20","22:00"],ext:"23:20"},
  {no:9,t:["7:40","11:20","15:15","18:45","22:30"],ext:"23:50"}
 ]},
 sunday:{label:"일요일(공휴일)",count:8,accent:"#e23b2e",rows:[
  {no:1,t:["5:00","8:10","12:00","15:40","19:10"]},
  {no:2,t:["5:25","8:40","12:25","16:05","19:40"]},
  {no:3,t:["5:50","9:10","12:50","16:30","20:10"]},
  {no:4,t:["6:15","9:40","13:20","17:00","20:40"]},
  {no:5,t:["6:40","10:10","13:50","17:30","21:10"]},
  {no:6,t:["7:05","10:40","14:20","17:55","21:40"],ext:"23:00"},
  {no:7,t:["7:30","11:05","14:50","18:20","22:05"],ext:"23:25"},
  {no:8,t:["7:50","11:30","15:15","18:45","22:30"],ext:"23:50"}
 ]}
};
function rev91RequestedSeason(now=new Date()){
 const forced=new URLSearchParams(location.search).get("season");
 if(forced==="summer"||forced==="autumn")return forced;
 return now>=new Date(2026,8,1,0,0,0)?"autumn":"summer";
}
let rev91Season=rev91RequestedSeason();
let DATA=rev91Season==="autumn"?AUTUMN_DATA:SUMMER_DATA;
'''

data_end = "};\nconst ORDER=[\"weekday\",\"saturday\",\"sunday\"];"
if text.count(data_end) != 1:
    raise RuntimeError("Rev90 timetable data end was not found exactly once")
text = text.replace(
    data_end,
    "};\n" + autumn_data + 'const ORDER=["weekday","saturday","sunday"];',
    1,
)

# The existing charter card has the right two times but its old wording contains a typo.
old_charter = '전세버스 <b>6:10</b> · 정차(약출발) · <b>18:00</b> 강남역 출발'
new_charter = '전세버스 <b>6:10</b> 경희대 출발 · <b>18:00</b> 강남역 출발'
if text.count(old_charter) != 2:
    raise RuntimeError("Rev90 charter description was not found exactly twice")
text = text.replace(old_charter, new_charter)

rev91_script = r'''

/* Rev91: preserve summer and automatically switch to the separate autumn data on Sep 1. */
function rev91ApplySeasonText(){
 const isAutumn=rev91Season==="autumn";
 const label=document.getElementById("season-label");
 const inspection=document.getElementById("inspection-days");
 if(label)label.textContent=isAutumn?"가을":"여름";
 if(inspection)inspection.textContent=isAutumn?"매주 월·목요일":"매주 월요일";
 document.title=`1560 ${isAutumn?"가을":"여름"} 시간표 앱 · Rev.91`;
}
function rev91SyncSeason(force){
 const wanted=rev91RequestedSeason();
 if(force||wanted!==rev91Season){
  rev91Season=wanted;
  DATA=rev91Season==="autumn"?AUTUMN_DATA:SUMMER_DATA;
  rev91ApplySeasonText();
  state.day=todayKey();
  render();
  if(typeof rev90MarkTodayTab==="function")rev90MarkTodayTab();
 }
}
rev91ApplySeasonText();
document.addEventListener("visibilitychange",()=>{if(!document.hidden)rev91SyncSeason(true)});
window.addEventListener("pageshow",()=>rev91SyncSeason(true));
setInterval(()=>rev91SyncSeason(false),30000);
setTimeout(()=>rev91SyncSeason(true),0);
'''
if "</body>" not in text:
    raise RuntimeError("Document body is missing")
text = text.replace("</body>", "<script>" + rev91_script + "</script>\n</body>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev91-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="91";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
