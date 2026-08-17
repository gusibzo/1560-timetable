from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev60.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.60", "Rev.61")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=60",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=61",{updateViaCache:"none"})',
    1,
)

# Rev61: the work-tracking button is now an entry point to the calendar.
# Tapping a calendar date directly toggles that date as a work day, changes
# its background color, and immediately recalculates the monthly count.
css = r'''
/* Rev61: direct tap-to-mark work calendar. */
.rev58-work-panel{
  grid-template-columns:minmax(0,1fr)!important;
}
.rev58-work-toggle{
  display:none!important;
}
.rev61-work-tip{
  display:block;
  margin-top:4px;
  color:#177226;
  font-size:10px;
  font-weight:950;
  line-height:1.25;
}
.calendar-day.rev58-work-day{
  background:#dff3e3!important;
  box-shadow:inset 0 0 0 2px rgba(23,114,38,.58),0 1px 0 #dfe3e8!important;
}
.calendar-day.rev58-work-day.selected{
  background:#c9ebd0!important;
  box-shadow:inset 0 0 0 2px #177226,0 0 0 2px rgba(23,114,38,.20)!important;
}
.calendar-day.rev58-work-day .solar-no{
  font-weight:950!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

old_today_click = '''btn.addEventListener("click",()=>{
    const d=new Date();
    rev58SetWork(d,!rev58IsWork(d));
    rev58Refresh();
    if(document.getElementById("calendarModal")?.classList.contains("open"))drawCalendar();
  });'''
new_today_click = '''btn.addEventListener("click",()=>{
    const d=new Date();
    calPicked=new Date(d);
    calView=new Date(d.getFullYear(),d.getMonth(),1);
    openCalendar();
  });'''
if old_today_click not in text:
    raise RuntimeError("Rev58 today-work click handler not found")
text = text.replace(old_today_click, new_today_click, 1)

old_day_click = 'b.addEventListener("click",()=>{calPicked=new Date(d);calView=new Date(d.getFullYear(),d.getMonth(),1);selectedText(d);drawCalendar()});'
new_day_click = 'b.addEventListener("click",()=>{calPicked=new Date(d);calView=new Date(d.getFullYear(),d.getMonth(),1);rev58SetWork(d,!rev58IsWork(d));selectedText(d);drawCalendar();rev58Refresh()});'
if old_day_click not in text:
    raise RuntimeError("calendar date click handler not found")
text = text.replace(old_day_click, new_day_click, 1)

old_panel = 'panel.innerHTML=`<div class="rev58-work-summary">월간 근무기록<strong id="rev58-work-count">이번 달 0일</strong><span id="rev60-work-start" class="rev60-work-start">기록 시작 · 2026.8.17</span></div><button type="button" id="rev58-work-toggle" class="rev58-work-toggle">선택 날짜 근무</button>`;'
new_panel = 'panel.innerHTML=`<div class="rev58-work-summary">월간 근무기록<strong id="rev58-work-count">이번 달 0일</strong><span id="rev60-work-start" class="rev60-work-start">기록 시작 · 2026.8.17</span><span class="rev61-work-tip">날짜를 누르면 근무일 체크 / 해제</span></div><button type="button" id="rev58-work-toggle" class="rev58-work-toggle">선택 날짜 근무</button>`;'
if old_panel not in text:
    raise RuntimeError("Rev60 calendar work panel markup not found")
text = text.replace(old_panel, new_panel, 1)

old_button = 'btn.textContent=worked?`✅ 오늘 근무 체크됨 · 8/17부터 · 이번 달 ${count}일`:`🚌 오늘 근무 체크 · 8/17부터 · 이번 달 ${count}일`;'
new_button = 'btn.textContent=worked?`✅ 오늘부터 체크됨 · 달력 열기 · 이번 달 ${count}일`:`📅 근무일 달력 열기 · 8/17부터 · 이번 달 ${count}일`;'
if old_button not in text:
    raise RuntimeError("Rev60 work button text not found")
text = text.replace(old_button, new_button, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev61-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="61";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
