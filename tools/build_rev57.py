from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev56.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.56", "Rev.57")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=56",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=57",{updateViaCache:"none"})',
    1,
)

# Rev57: first time-saving dashboard. Keep it route-level and factual:
# today's actual schedule, current departed trip, next departure, remaining
# departures, and final departure. It always follows todayKey(), so browsing
# another tab does not change the live briefing.
css = r'''
/* Rev57: compact today work briefing. */
.rev57-briefing{
  margin-top:11px;
  padding:12px;
  border-radius:15px;
  background:#171a1f;
  color:#fff;
  box-shadow:0 8px 22px rgba(0,0,0,.20),inset 0 1px 0 rgba(255,255,255,.07);
}
.rev57-briefing-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
  margin-bottom:9px;
}
.rev57-briefing-title{
  font-size:13px;
  font-weight:950;
  letter-spacing:-.25px;
}
.rev57-briefing-badge{
  flex:0 0 auto;
  padding:4px 8px;
  border-radius:999px;
  background:rgba(255,255,255,.10);
  color:#dce2ea;
  font-size:9.5px;
  font-weight:900;
  white-space:nowrap;
}
.rev57-briefing-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:7px;
}
.rev57-briefing-item{
  min-width:0;
  padding:9px 9px 8px;
  border-radius:11px;
  background:#242930;
  border:1px solid rgba(255,255,255,.055);
}
.rev57-briefing-k{
  display:block;
  color:#9fa8b5;
  font-size:9px;
  font-weight:850;
  line-height:1.1;
}
.rev57-briefing-v{
  display:block;
  margin-top:4px;
  color:#fff;
  font-size:12.5px;
  font-weight:950;
  line-height:1.25;
  letter-spacing:-.35px;
  overflow-wrap:anywhere;
}
#rev57-current{color:#baff64}
#rev57-next{color:#ffe278}
#rev57-remaining{color:#7ee8ff}
#rev57-last{color:#ff9d91}
@media(max-width:360px){
  .rev57-briefing{padding:10px}
  .rev57-briefing-grid{gap:6px}
  .rev57-briefing-item{padding:8px 7px}
  .rev57-briefing-v{font-size:11.5px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev57: live route-level work briefing for today's real schedule. */
function rev57EnsureBriefing(){
  let box=document.getElementById("rev57-briefing");
  if(box)return box;
  box=document.createElement("section");
  box.id="rev57-briefing";
  box.className="rev57-briefing";
  box.setAttribute("aria-label","오늘 근무 브리핑");
  box.innerHTML=`
    <div class="rev57-briefing-head">
      <span class="rev57-briefing-title">🚌 오늘 근무 브리핑</span>
      <span id="rev57-day" class="rev57-briefing-badge">오늘 시간표</span>
    </div>
    <div class="rev57-briefing-grid">
      <div class="rev57-briefing-item"><span class="rev57-briefing-k">현재 출발</span><strong id="rev57-current" class="rev57-briefing-v">—</strong></div>
      <div class="rev57-briefing-item"><span class="rev57-briefing-k">다음 출발</span><strong id="rev57-next" class="rev57-briefing-v">—</strong></div>
      <div class="rev57-briefing-item"><span class="rev57-briefing-k">남은 출발</span><strong id="rev57-remaining" class="rev57-briefing-v">—</strong></div>
      <div class="rev57-briefing-item"><span class="rev57-briefing-k">막차 출발</span><strong id="rev57-last" class="rev57-briefing-v">—</strong></div>
    </div>`;
  const notice=document.querySelector(".notice");
  const board=document.querySelector(".board");
  if(notice)notice.insertAdjacentElement("afterend",box);
  else if(board&&board.parentNode)board.parentNode.insertBefore(box,board);
  else (document.querySelector("main")||document.querySelector(".wrap")||document.body).appendChild(box);
  return box;
}
function rev57EventText(ev){
  if(!ev)return "—";
  const bus=`${ev.ri+1}번`;
  if(ev.kind==="ext")return `${bus} · 추가 ${ev.time}`;
  return `${bus} · ${ev.ci+1}회 ${ev.time}`;
}
function rev57TodayEvents(day){
  if(typeof rev23Events==="function")return rev23Events(day);
  const events=[];
  const data=DATA[day];
  if(!data)return events;
  data.rows.forEach((row,ri)=>{
    row.t.forEach((time,ci)=>{if(time)events.push({time,min:toMin(time),ri,ci,kind:"base"});});
    if(row.ext)events.push({time:row.ext,min:toMin(row.ext),ri,ci:4,kind:"ext"});
  });
  return events.sort((a,b)=>a.min-b.min);
}
function rev57SyncBriefing(){
  rev57EnsureBriefing();
  const day=todayKey();
  const data=DATA[day];
  if(!data)return;
  const events=rev57TodayEvents(day);
  const now=new Date();
  const nowMin=now.getHours()*60+now.getMinutes()+now.getSeconds()/60;
  let current=null,next=null;
  for(const ev of events){
    if(ev.min<=nowMin)current=ev;
    else{next=ev;break;}
  }
  const remaining=events.filter(ev=>ev.min>nowMin).length;
  const last=events.length?events[events.length-1]:null;
  const dayEl=document.getElementById("rev57-day");
  const currentEl=document.getElementById("rev57-current");
  const nextEl=document.getElementById("rev57-next");
  const remainingEl=document.getElementById("rev57-remaining");
  const lastEl=document.getElementById("rev57-last");
  if(dayEl)dayEl.textContent=`${data.label} · ${data.count}대`;
  if(currentEl)currentEl.textContent=current?rev57EventText(current):"운행 전";
  if(nextEl)nextEl.textContent=next?rev57EventText(next):"오늘 운행 종료";
  if(remainingEl)remainingEl.textContent=`${remaining}회`;
  if(lastEl)lastEl.textContent=last?last.time:"—";
}
setInterval(rev57SyncBriefing,1000);
setTimeout(rev57SyncBriefing,50);
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev57-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="57";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
