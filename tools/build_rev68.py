from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev67.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.67", "Rev.68")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=67",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=68",{updateViaCache:"none"})',
    1,
)

# Rev68: horizontal monthly full-attendance summary.
# Count every date in the displayed month. Each weekday total is the
# selected rest day plus its immediately previous weekday.
css = r'''
/* Rev68: horizontal, auto-calculated monthly full-attendance summary. */
.rev67-full-attendance{
  margin:10px 0 8px!important;
  padding:9px 8px 8px!important;
  overflow:hidden!important;
}
.rev67-full-attendance-title{
  margin-bottom:7px!important;
}
.rev68-full-month{
  color:#177226;
  font-size:11px;
  font-weight:950;
  white-space:nowrap;
}
.rev68-full-grid{
  display:grid;
  grid-template-columns:repeat(7,minmax(0,1fr));
  overflow:hidden;
  border:1px solid #d8dde3;
  border-radius:10px;
  background:#fff;
  font-variant-numeric:tabular-nums;
}
.rev68-full-cell{
  min-width:0;
  text-align:center;
  border-right:1px solid #e4e8ec;
}
.rev68-full-cell:last-child{border-right:0}
.rev68-full-day{
  padding:5px 1px 2px;
  background:#f4f6f8;
  color:#3b4650;
  font-size:10px;
  font-weight:950;
}
.rev68-full-total{
  padding:3px 1px 2px;
  color:#177226;
  font-size:17px;
  font-weight:950;
  line-height:1;
}
.rev68-full-total::after{
  content:"일";
  margin-left:1px;
  font-size:8px;
  font-weight:900;
}
.rev68-full-rule{
  padding:2px 0 5px;
  color:#697581;
  font-size:7.5px;
  font-weight:850;
  letter-spacing:-.45px;
  white-space:nowrap;
}
/* 토요일은 글자·숫자·계산표시 모두 파랑, 일요일은 모두 빨강 */
.rev68-full-cell:nth-child(6) .rev68-full-day,
.rev68-full-cell:nth-child(6) .rev68-full-total,
.rev68-full-cell:nth-child(6) .rev68-full-rule{color:#1767c8!important}
.rev68-full-cell:nth-child(7) .rev68-full-day,
.rev68-full-cell:nth-child(7) .rev68-full-total,
.rev68-full-cell:nth-child(7) .rev68-full-rule{color:#df3a43!important}
@media(max-width:360px){
  .rev68-full-total{font-size:15px}
  .rev68-full-rule{font-size:6.8px;letter-spacing:-.6px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev68: calculate the horizontal summary whenever the calendar month changes. */
function rev68WeekdayCounts(y,m){
  const counts=[0,0,0,0,0,0,0]; // Sun..Sat
  const last=new Date(y,m+1,0).getDate();
  for(let day=1;day<=last;day++){
    counts[new Date(y,m,day).getDay()]++;
  }
  return counts;
}
function rev68FullAttendanceTotals(y,m){
  const c=rev68WeekdayCounts(y,m);
  const targets=[1,2,3,4,5,6,0]; // Mon..Sun
  return targets.map(day=>c[(day+6)%7]+c[day]);
}
function rev68RenderFullAttendance(){
  if(typeof calView==="undefined"||!calView)return;
  const box=typeof rev67EnsureFullAttendanceTable==="function"?rev67EnsureFullAttendanceTable():document.getElementById("rev67-full-attendance");
  if(!box)return;
  const y=calView.getFullYear(),m=calView.getMonth();
  const totals=rev68FullAttendanceTotals(y,m);
  const days=["월","화","수","목","금","토","일"];
  const rules=["일+월","월+화","화+수","수+목","목+금","금+토","토+일"];
  box.setAttribute("aria-label",`${y}년 ${m+1}월 만근 합계`);
  box.innerHTML=`
    <div class="rev67-full-attendance-title">
      <span>✅ 만근 합계</span>
      <span class="rev68-full-month">${y}.${m+1}</span>
    </div>
    <div class="rev68-full-grid">
      ${days.map((day,i)=>`<div class="rev68-full-cell"><div class="rev68-full-day">${day}</div><div class="rev68-full-total">${totals[i]}</div><div class="rev68-full-rule">${rules[i]}</div></div>`).join("")}
    </div>`;
}
const rev68BaseDrawCalendar=drawCalendar;
drawCalendar=function(){
  rev68BaseDrawCalendar();
  rev68RenderFullAttendance();
};
setTimeout(rev68RenderFullAttendance,100);
setInterval(()=>{
  if(document.getElementById("calendarModal")?.classList.contains("open"))rev68RenderFullAttendance();
},700);
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev68-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="68";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
