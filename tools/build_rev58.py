from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev57.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.57", "Rev.58")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=57",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=58",{updateViaCache:"none"})',
    1,
)

# Rev58: manual work-day tracking stored on the driver's device. Add a
# one-tap today button to the live briefing and integrate monthly work count,
# selected-date toggle, and bus markers into the existing calendar.
css = r'''
/* Rev58: monthly work-day tracker integrated into the existing calendar. */
.rev58-today-work{
  width:100%;
  margin-top:8px;
  border:0;
  border-radius:11px;
  padding:10px 12px;
  background:#2f3741;
  color:#fff;
  font:950 12px/1 inherit;
  cursor:pointer;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08);
}
.rev58-today-work.checked{
  background:#177226;
  color:#fff;
}
.rev58-work-panel{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:9px;
  align-items:center;
  margin-top:10px;
  padding:10px 11px;
  border-radius:13px;
  background:#e9f6ec;
  border:1px solid #c9e7cf;
  box-shadow:0 1px 0 rgba(0,0,0,.04);
}
.rev58-work-summary{
  min-width:0;
  color:#33403a;
  font-size:10px;
  font-weight:850;
  line-height:1.25;
}
.rev58-work-summary strong{
  display:block;
  margin-top:2px;
  color:#177226;
  font-size:16px;
  font-weight:950;
  letter-spacing:-.4px;
}
.rev58-work-toggle{
  border:0;
  border-radius:10px;
  padding:9px 10px;
  background:#177226;
  color:#fff;
  font:950 11px/1 inherit;
  cursor:pointer;
  white-space:nowrap;
}
.rev58-work-toggle.checked{background:#374151}
.calendar-day.rev58-work-day::after{
  content:"🚌";
  position:absolute;
  right:3px;
  bottom:2px;
  z-index:3;
  font-size:12px;
  line-height:1;
  filter:drop-shadow(0 1px 1px rgba(0,0,0,.16));
}
.calendar-day.rev58-work-day{
  box-shadow:inset 0 0 0 2px rgba(23,114,38,.42),0 1px 0 #dfe3e8;
}
.calendar-day.today.rev58-work-day{
  box-shadow:inset 0 0 0 2px rgba(255,255,255,.82),0 0 0 2px rgba(23,114,38,.48);
}
.calendar-legend .rev58-legend-bus{font-size:12px;line-height:1}
@media(max-width:360px){
  .rev58-work-panel{padding:8px 9px;gap:7px}
  .rev58-work-summary strong{font-size:14px}
  .rev58-work-toggle{padding:8px 8px;font-size:10px}
  .calendar-day.rev58-work-day::after{font-size:10px;right:2px;bottom:2px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev58: work-day records stay on this device using localStorage. */
const rev58WorkStorageKey="1560-work-days-v1";
let rev58WorkDays={};
try{
  const saved=localStorage.getItem(rev58WorkStorageKey);
  const parsed=saved?JSON.parse(saved):{};
  if(parsed&&typeof parsed==="object"&&!Array.isArray(parsed))rev58WorkDays=parsed;
}catch(_){rev58WorkDays={};}
function rev58DateKey(d){
  const p=n=>String(n).padStart(2,"0");
  return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}`;
}
function rev58Save(){
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
}
function rev58EnsureTodayButton(){
  const box=typeof rev57EnsureBriefing==="function"?rev57EnsureBriefing():document.getElementById("rev57-briefing");
  if(!box)return null;
  let btn=document.getElementById("rev58-today-work");
  if(btn)return btn;
  btn=document.createElement("button");
  btn.id="rev58-today-work";
  btn.type="button";
  btn.className="rev58-today-work";
  btn.addEventListener("click",()=>{
    const d=new Date();
    rev58SetWork(d,!rev58IsWork(d));
    rev58Refresh();
    if(document.getElementById("calendarModal")?.classList.contains("open"))drawCalendar();
  });
  box.appendChild(btn);
  return btn;
}
function rev58EnsureCalendarPanel(){
  const week=document.querySelector(".calendar-week");
  if(!week)return null;
  let panel=document.getElementById("rev58-work-panel");
  if(!panel){
    panel=document.createElement("div");
    panel.id="rev58-work-panel";
    panel.className="rev58-work-panel";
    panel.innerHTML=`<div class="rev58-work-summary">월간 근무기록<strong id="rev58-work-count">이번 달 0일</strong></div><button type="button" id="rev58-work-toggle" class="rev58-work-toggle">선택 날짜 근무</button>`;
    week.parentNode.insertBefore(panel,week);
    document.getElementById("rev58-work-toggle").addEventListener("click",()=>{
      const d=calPicked?new Date(calPicked):new Date();
      rev58SetWork(d,!rev58IsWork(d));
      drawCalendar();
      rev58Refresh();
    });
  }
  const legend=document.querySelector(".calendar-legend");
  if(legend&&!legend.querySelector(".rev58-work-legend")){
    const item=document.createElement("span");
    item.className="legend-item rev58-work-legend";
    item.innerHTML='<span class="rev58-legend-bus">🚌</span>근무';
    legend.appendChild(item);
  }
  return panel;
}
function rev58DecorateCalendar(){
  rev58EnsureCalendarPanel();
  const y=calView.getFullYear(),m=calView.getMonth();
  const count=document.getElementById("rev58-work-count");
  if(count)count.textContent=`${m+1}월 근무 ${rev58MonthCount(y,m)}일`;
  document.querySelectorAll("#calendarGrid .calendar-day").forEach(btn=>{
    const label=btn.getAttribute("aria-label")||"";
    const match=label.match(/(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일/);
    if(!match)return;
    const d=new Date(Number(match[1]),Number(match[2])-1,Number(match[3]));
    const worked=rev58IsWork(d);
    btn.classList.toggle("rev58-work-day",worked);
    if(worked&&!label.includes("근무일"))btn.setAttribute("aria-label",`${label}, 근무일`);
  });
  const picked=calPicked?new Date(calPicked):new Date();
  const toggle=document.getElementById("rev58-work-toggle");
  if(toggle){
    const worked=rev58IsWork(picked);
    toggle.classList.toggle("checked",worked);
    toggle.textContent=worked?"✅ 근무일 해제":"🚌 근무일로 체크";
    toggle.setAttribute("aria-pressed",worked?"true":"false");
  }
  if(typeof calendarSelected!=="undefined"&&calendarSelected){
    const key=rev58DateKey(picked);
    const marker=rev58IsWork(picked)?" · 🚌 근무":"";
    if(!calendarSelected.querySelector(".rev58-selected-work")){
      const span=document.createElement("span");
      span.className="rev58-selected-work";
      span.style.fontWeight="950";
      span.style.color="#177226";
      calendarSelected.appendChild(span);
    }
    const span=calendarSelected.querySelector(".rev58-selected-work");
    if(span)span.textContent=marker;
  }
}
const rev58BaseDrawCalendar=drawCalendar;
drawCalendar=function(){
  rev58BaseDrawCalendar();
  rev58DecorateCalendar();
};
function rev58Refresh(){
  const btn=rev58EnsureTodayButton();
  if(btn){
    const today=new Date();
    const worked=rev58IsWork(today);
    const count=rev58MonthCount(today.getFullYear(),today.getMonth());
    btn.classList.toggle("checked",worked);
    btn.setAttribute("aria-pressed",worked?"true":"false");
    btn.textContent=worked?`✅ 오늘 근무 체크됨 · 이번 달 ${count}일`:`🚌 오늘 근무 체크 · 이번 달 ${count}일`;
  }
  if(document.getElementById("calendarModal")?.classList.contains("open"))rev58DecorateCalendar();
}
setInterval(rev58Refresh,1500);
setTimeout(rev58Refresh,80);
'''
pos = text.rfind("</script>")
if pos == -1:
    raise RuntimeError("index.html script closing tag not found")
text = text[:pos] + js + "\n" + text[pos:]
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev58-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="58";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
