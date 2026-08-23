from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev66.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.66", "Rev.67")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=66",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=67",{updateViaCache:"none"})',
    1,
)

# Rev67: add the approved full-attendance reference table above the calendar.
# Rule: each weekday's full-attendance pair includes that day and the previous day.
css = r'''
/* Rev67: compact full-attendance guide above the calendar. */
.rev67-full-attendance{
  margin:10px 0 8px;
  padding:9px 10px 10px;
  border:1px solid #cfd6dd;
  border-radius:13px;
  background:linear-gradient(180deg,#f9fbfc 0%,#eef2f5 100%);
  box-shadow:0 1px 0 rgba(0,0,0,.04);
}
.rev67-full-attendance-title{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
  margin-bottom:7px;
  color:#177226;
  font-size:13px;
  font-weight:950;
}
.rev67-full-attendance-title small{
  color:#65717d;
  font-size:9px;
  font-weight:850;
}
.rev67-full-attendance-table{
  width:100%;
  border-collapse:separate;
  border-spacing:0;
  overflow:hidden;
  border:1px solid #d8dde3;
  border-radius:10px;
  background:#fff;
  font-variant-numeric:tabular-nums;
}
.rev67-full-attendance-table th,
.rev67-full-attendance-table td{
  padding:6px 8px;
  border-bottom:1px solid #e4e8ec;
  text-align:center;
  line-height:1.15;
}
.rev67-full-attendance-table tr:last-child th,
.rev67-full-attendance-table tr:last-child td{border-bottom:0}
.rev67-full-attendance-table th{
  width:47%;
  background:#f4f6f8;
  color:#2f3943;
  font-size:11px;
  font-weight:950;
}
.rev67-full-attendance-table td{
  color:#177226;
  font-size:12px;
  font-weight:950;
}
.rev67-full-attendance-table tr:first-child th,
.rev67-full-attendance-table tr:first-child td{
  background:#fffbe6;
}
@media(max-width:360px){
  .rev67-full-attendance{padding:8px 8px 9px}
  .rev67-full-attendance-table th,
  .rev67-full-attendance-table td{padding:5px 5px}
  .rev67-full-attendance-table th{font-size:10px}
  .rev67-full-attendance-table td{font-size:11px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev67: full-attendance guide shown at the top of the calendar content. */
function rev67EnsureFullAttendanceTable(){
  const week=document.querySelector(".calendar-week");
  if(!week)return null;
  let box=document.getElementById("rev67-full-attendance");
  if(box)return box;
  box=document.createElement("section");
  box.id="rev67-full-attendance";
  box.className="rev67-full-attendance";
  box.setAttribute("aria-label","요일별 만근 기준표");
  box.innerHTML=`
    <div class="rev67-full-attendance-title"><span>✅ 만근 기준표</span><small>해당 요일 + 바로 전 요일</small></div>
    <table class="rev67-full-attendance-table">
      <tbody>
        <tr><th scope="row">월요일 만근</th><td>일 + 월</td></tr>
        <tr><th scope="row">화요일 만근</th><td>월 + 화</td></tr>
        <tr><th scope="row">수요일 만근</th><td>화 + 수</td></tr>
        <tr><th scope="row">목요일 만근</th><td>수 + 목</td></tr>
        <tr><th scope="row">금요일 만근</th><td>목 + 금</td></tr>
        <tr><th scope="row">토요일 만근</th><td>금 + 토</td></tr>
        <tr><th scope="row">일요일 만근</th><td>토 + 일</td></tr>
      </tbody>
    </table>`;
  const workPanel=document.getElementById("rev58-work-panel");
  const anchor=workPanel||week;
  anchor.parentNode.insertBefore(box,anchor);
  return box;
}
const rev67BaseDrawCalendar=drawCalendar;
drawCalendar=function(){
  rev67BaseDrawCalendar();
  rev67EnsureFullAttendanceTable();
};
setTimeout(rev67EnsureFullAttendanceTable,80);
setInterval(()=>{
  if(document.getElementById("calendarModal")?.classList.contains("open"))rev67EnsureFullAttendanceTable();
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev67-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="67";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
