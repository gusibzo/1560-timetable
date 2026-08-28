from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev87.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.87", "Rev.88")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=87",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=88",{updateViaCache:"none"})',
    1,
)

# Keep the calendar label short enough to share the yellow clock row with the
# live time. The full work-day details remain available to screen readers.
old_refresh = '    btn.textContent=worked?`✅ 오늘부터 체크됨 · 달력 열기 · 이번 달 ${count}일`:`📅 근무일 달력 열기 · 8/17부터 · 이번 달 ${count}일`;'
new_refresh = '''    btn.textContent="📅 근무일 달력";
    btn.setAttribute("aria-label",worked?`근무일 달력 열기 · 오늘 근무 체크됨 · 이번 달 ${count}일`:`근무일 달력 열기 · 8/17부터 · 이번 달 ${count}일`);'''
if text.count(old_refresh) != 1:
    raise RuntimeError("Rev87 calendar refresh label was not found exactly once")
text = text.replace(old_refresh, new_refresh, 1)

old_selected_refresh = '  btn.textContent=`📅 근무일 달력 열기 · 8/17부터 · 이번 달 ${count}일`;'
new_selected_refresh = '''  btn.textContent="📅 근무일 달력";
  btn.setAttribute("aria-label",`근무일 달력 열기 · 8/17부터 · 이번 달 ${count}일`);'''
if text.count(old_selected_refresh) != 1:
    raise RuntimeError("Rev87 selected-bus calendar label was not found exactly once")
text = text.replace(old_selected_refresh, new_selected_refresh, 1)

rev88_css = '''

/* Rev88: dock the black work-calendar button inside the yellow clock row. */
.clock{gap:8px!important}
.clock .live{display:none!important}
.clock #rev58-today-work.rev88-clock-calendar,
.clock #rev58-today-work.rev88-clock-calendar.checked{
  position:relative!important;
  flex:1 1 auto!important;
  width:auto!important;
  min-width:0!important;
  min-height:36px!important;
  margin:0!important;
  padding:8px 9px!important;
  border:1px solid rgba(255,255,255,.20)!important;
  border-radius:10px!important;
  background:linear-gradient(180deg,#3d4652,#252c35)!important;
  color:#fff!important;
  font:950 12px/1.1 inherit!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  box-shadow:0 2px 0 rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.12)!important;
}
.clock #now{flex:0 0 auto!important;margin-left:auto!important}
#rev57-briefing{display:none!important}
@media(max-width:380px){
  .clock{gap:6px!important}
  .clock #rev58-today-work.rev88-clock-calendar,
  .clock #rev58-today-work.rev88-clock-calendar.checked{
    padding:8px 7px!important;
    font-size:11px!important;
  }
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev88_css + "</style>", 1)

rev88_script = '''

/* Rev88: move the existing calendar control into the live clock row. */
function rev88DockCalendarInClock(){
  const clock=document.querySelector(".clock");
  const now=document.getElementById("now");
  const btn=typeof rev58EnsureTodayButton==="function"?rev58EnsureTodayButton():document.getElementById("rev58-today-work");
  if(!clock||!now||!btn)return;
  btn.classList.add("rev88-clock-calendar");
  if(btn.parentElement!==clock)clock.insertBefore(btn,now);
}
rev88DockCalendarInClock();
setTimeout(rev88DockCalendarInClock,100);
setInterval(rev88DockCalendarInClock,1500);
'''
if "</body>" not in text:
    raise RuntimeError("Document body is missing")
text = text.replace("</body>", "<script>" + rev88_script + "</script>\n</body>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev88-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="88";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
