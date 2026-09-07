from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev117.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.117", "Rev.118")

rev118_css = r'''

/* Rev118: morning / afternoon work-shift cycle. */
.rev58-work-summary strong{
  font-size:14px!important;
  letter-spacing:-.45px!important;
  white-space:nowrap;
}
.rev61-work-tip{
  color:#46515c!important;
}
.calendar-day.rev58-work-day.rev118-work-am{
  background:#dff3e3!important;
  box-shadow:inset 0 0 0 2px rgba(23,114,38,.62),0 1px 0 #dfe3e8!important;
}
.calendar-day.rev58-work-day.rev118-work-pm{
  background:#dcecff!important;
  box-shadow:inset 0 0 0 2px rgba(23,103,200,.62),0 1px 0 #dfe3e8!important;
}
.calendar-day.rev58-work-day.rev118-work-am.selected{
  background:#c9ebd0!important;
  box-shadow:inset 0 0 0 2px #177226,0 0 0 2px rgba(23,114,38,.20)!important;
}
.calendar-day.rev58-work-day.rev118-work-pm.selected{
  background:#c7e0ff!important;
  box-shadow:inset 0 0 0 2px #1767c8,0 0 0 2px rgba(23,103,200,.20)!important;
}
.calendar-day.rev118-work-am::after,
.calendar-day.rev118-work-pm::after{
  right:2px!important;
  bottom:2px!important;
  padding:2px 3px;
  border-radius:5px;
  color:#fff;
  font-size:7.5px!important;
  font-weight:950;
  line-height:1!important;
  filter:none!important;
}
.calendar-day.rev118-work-am::after{
  content:"오전"!important;
  background:#177226;
}
.calendar-day.rev118-work-pm::after{
  content:"오후"!important;
  background:#1767c8;
}
.rev58-work-legend{
  gap:4px!important;
}
.rev118-legend-chip{
  display:inline-flex;
  align-items:center;
  border-radius:5px;
  padding:2px 4px;
  color:#fff;
  font-size:8px;
  font-weight:950;
  line-height:1;
}
.rev118-legend-am{background:#177226}
.rev118-legend-pm{background:#1767c8}
@media(max-width:360px){
  .rev58-work-summary strong{font-size:12.5px!important}
  .calendar-day.rev118-work-am::after,
  .calendar-day.rev118-work-pm::after{font-size:7px!important;padding:2px}
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev118_css + "</style>", 1)

old_work_functions = r'''function rev58Save(){
  try{localStorage.setItem(rev58WorkStorageKey,JSON.stringify(rev58WorkDays));}catch(_){}
}
function rev58IsWork(d){return !!rev58WorkDays[rev58DateKey(d)];}
function rev58SetWork(d,value){
  const key=rev58DateKey(d);
  if(value)rev58WorkDays[key]=1;else delete rev58WorkDays[key];
  rev58Save();
}
function rev58MonthCount(y,m){
  const prefix=`${y}-${String(m+1).padStart(2,"0")}-`;
  return Object.keys(rev58WorkDays).filter(key=>key.startsWith(prefix)&&rev58WorkDays[key]).length;
}'''
new_work_functions = r'''function rev58Save(){
  try{localStorage.setItem(rev58WorkStorageKey,JSON.stringify(rev58WorkDays));}catch(_){}
}
/* Existing green work days become morning shifts without losing any records. */
Object.keys(rev58WorkDays).forEach(key=>{
  const value=rev58WorkDays[key];
  if(value===1||value===true||value==="1")rev58WorkDays[key]="am";
  else if(value!=="am"&&value!=="pm")delete rev58WorkDays[key];
});
rev58Save();
function rev118Shift(d){
  const value=rev58WorkDays[rev58DateKey(d)];
  return value==="pm"?"pm":value?"am":"";
}
function rev58IsWork(d){return !!rev118Shift(d);}
function rev58SetWork(d,value){
  const key=rev58DateKey(d);
  if(value){
    if(!rev118Shift(d))rev58WorkDays[key]="am";
  }else delete rev58WorkDays[key];
  rev58Save();
}
function rev118CycleShift(d){
  const key=rev58DateKey(d),shift=rev118Shift(d);
  if(!shift)rev58WorkDays[key]="am";
  else if(shift==="am")rev58WorkDays[key]="pm";
  else delete rev58WorkDays[key];
  rev58Save();
}
function rev58MonthCount(y,m){
  const prefix=`${y}-${String(m+1).padStart(2,"0")}-`;
  return Object.keys(rev58WorkDays).filter(key=>key.startsWith(prefix)&&rev58WorkDays[key]).length;
}
function rev118MonthShiftCounts(y,m){
  const prefix=`${y}-${String(m+1).padStart(2,"0")}-`;
  let am=0,pm=0;
  Object.keys(rev58WorkDays).forEach(key=>{
    if(!key.startsWith(prefix))return;
    const shift=rev58WorkDays[key];
    if(shift==="pm")pm++;else if(shift)am++;
  });
  return {am,pm,total:am+pm};
}'''
if text.count(old_work_functions) != 1:
    raise RuntimeError("Rev117 work-day functions were not found exactly once")
text = text.replace(old_work_functions, new_work_functions, 1)

old_click = "rev58SetWork(d,!rev58IsWork(d));"
if text.count(old_click) != 2:
    raise RuntimeError("Rev117 work-day click handlers were not found exactly twice")
text = text.replace(old_click, "rev118CycleShift(d);")

old_tip = '<span class="rev61-work-tip">날짜를 누르면 근무일 체크 / 해제</span>'
new_tip = '<span class="rev61-work-tip">날짜를 누르면 오전 → 오후 → 해제</span>'
if text.count(old_tip) != 1:
    raise RuntimeError("Rev117 work-day tip was not found exactly once")
text = text.replace(old_tip, new_tip, 1)

old_legend = "item.innerHTML='<span class=\"rev58-legend-bus\">🚌</span>근무';"
new_legend = "item.innerHTML='<span class=\"rev118-legend-chip rev118-legend-am\">오전</span><span class=\"rev118-legend-chip rev118-legend-pm\">오후</span>';"
if text.count(old_legend) != 1:
    raise RuntimeError("Rev117 work legend was not found exactly once")
text = text.replace(old_legend, new_legend, 1)

new_decorate = r'''function rev58DecorateCalendar(){
  rev58EnsureCalendarPanel();
  const y=calView.getFullYear(),m=calView.getMonth();
  const counts=rev118MonthShiftCounts(y,m);
  const count=document.getElementById("rev58-work-count");
  if(count)count.textContent=`${m+1}월 오전 ${counts.am}일 · 오후 ${counts.pm}일 · 전체 ${counts.total}일`;
  document.querySelectorAll("#calendarGrid .calendar-day").forEach(btn=>{
    const label=btn.getAttribute("aria-label")||"";
    const match=label.match(/(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일/);
    if(!match)return;
    const d=new Date(Number(match[1]),Number(match[2])-1,Number(match[3]));
    const shift=rev118Shift(d),worked=!!shift;
    btn.classList.toggle("rev58-work-day",worked);
    btn.classList.toggle("rev118-work-am",shift==="am");
    btn.classList.toggle("rev118-work-pm",shift==="pm");
    const cleanLabel=label.replace(/, (?:오전근무|오후근무|근무일)$/,'');
    btn.setAttribute("aria-label",shift?`${cleanLabel}, ${shift==="am"?"오전근무":"오후근무"}`:cleanLabel);
  });
  const picked=calPicked?new Date(calPicked):new Date();
  const shift=rev118Shift(picked);
  const toggle=document.getElementById("rev58-work-toggle");
  if(toggle){
    toggle.classList.toggle("checked",!!shift);
    toggle.textContent=!shift?"오전근무로 체크":shift==="am"?"오전 → 오후":"오후 → 해제";
    toggle.setAttribute("aria-pressed",shift?"true":"false");
  }
  if(typeof calendarSelected!=="undefined"&&calendarSelected){
    const marker=shift==="am"?" · 오전근무":shift==="pm"?" · 오후근무":"";
    if(!calendarSelected.querySelector(".rev58-selected-work")){
      const span=document.createElement("span");
      span.className="rev58-selected-work";
      span.style.fontWeight="950";
      calendarSelected.appendChild(span);
    }
    const span=calendarSelected.querySelector(".rev58-selected-work");
    if(span){
      span.textContent=marker;
      span.style.color=shift==="pm"?"#1767c8":"#177226";
    }
  }
}'''
pattern = r'function rev58DecorateCalendar\(\)\{.*?\n\}\nconst rev58BaseDrawCalendar'
replacement = new_decorate + "\nconst rev58BaseDrawCalendar"
text, replacements = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
if replacements != 1:
    raise RuntimeError("Rev117 calendar decoration function was not found exactly once")

old_registration = 'navigator.serviceWorker.register("./sw.js?v=117",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=118",{updateViaCache:"none"})'
if text.count(old_registration) != 1:
    raise RuntimeError("Rev117 service worker registration was not found exactly once")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev118-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="118";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
