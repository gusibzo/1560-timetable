from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
index = root / "index.html"
text = index.read_text(encoding="utf-8")

# Revision and requested labels/calendar.
text = re.sub(r"Rev\.(?:1[789]|2[0-2])", "Rev.23", text)
for old, new in {
    '일요일<span class="cnt">8대</span>': '일요일(공휴일)<span class="cnt">8대</span>',
    'sunday:{label:"일요일",count:8': 'sunday:{label:"일요일(공휴일)",count:8',
    '대한민국 음력·공휴일 달력': '대한민국 달력',
    '음력 · 공휴일 · 대체공휴일 · 주요 전통일 표시': '음력 · 공휴일 · 주요 전통일 표시',
}.items():
    text = text.replace(old, new)

# Open maps in the same browser tab so the phone Back button returns to the timetable.
text = text.replace(
    '<a class="naver" href="https://m.map.naver.com/" target="_blank" rel="noopener noreferrer">🗺️ 네이버지도</a>',
    '<a class="naver" href="https://m.map.naver.com/" rel="noopener noreferrer">🗺️ 네이버지도</a>',
)
text = text.replace(
    '.gps-actions .kakao{background:#fae100;color:#2d2000}',
    '.gps-actions .tmap{background:#111827;color:#fff}',
)
text = text.replace(
    '<a class="kakao" href="https://m.map.kakao.com/" target="_blank" rel="noopener noreferrer">🧭 카카오맵</a>',
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" rel="noopener noreferrer">🧭 T맵</a>',
)
text = text.replace(
    '<a class="naver" href="https://map.kakao.com/link/to/현재위치,37.5665,126.9780" target="_blank" rel="noopener noreferrer">🚏 길찾기 예시</a>',
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" rel="noopener noreferrer">🚏 T맵 길찾기</a>',
)
text = text.replace(
    '※ 휴대폰 브라우저 위치 권한이 꺼져 있으면 좌표를 불러오지 못할 수 있습니다.',
    '※ 지도를 본 뒤 휴대폰의 뒤로가기를 누르면 1560 시간표로 돌아옵니다.',
)

css = r'''
/* Rev23: persistent row highlight, elapsed counter, count in inspection row, bottom guide */
.seg[data-day="sunday"]{font-size:12px;letter-spacing:-.5px}
.chips{display:none!important}
.notice{display:grid!important;grid-template-columns:1fr auto 1fr;align-items:center;gap:10px}
.notice>span:first-child{text-align:left}
.notice>b:last-child{text-align:right}
.notice .service-count{display:inline-flex;align-items:center;justify-content:center;min-width:58px;padding:6px 12px;border-radius:999px;background:var(--brand);color:#fff;font-size:15px;font-weight:950;box-shadow:inset 0 1px 0 rgba(255,255,255,.18)}
body[data-day="sunday"] .grid td.edge{background:var(--brand)!important;color:#fff!important;border-top-color:#c62c25!important;box-shadow:inset 0 0 0 1px rgba(255,255,255,.18)}
body[data-day="sunday"] .grid td.edge .ext{color:#fff!important}
.next-countdown{display:block;width:max-content;max-width:100%;margin:4px auto 0;padding:2px 4px;border-radius:6px;background:#111827;color:#fff;font-size:8.5px;font-weight:950;line-height:1.15;white-space:nowrap;letter-spacing:-.2px}
.ext.next-ext{margin:4px auto 0;padding:3px 2px;border-radius:7px;background:var(--brand);color:#fff!important}
.ext.next-ext b{color:#fff!important}
.ext.next-ext .next-countdown{margin-top:3px;background:#fff;color:#111827}
body[data-day="sunday"] .next .time{background:var(--brand)!important;color:#fff!important}
.grid td.no{cursor:pointer;user-select:none;-webkit-user-select:none;touch-action:manipulation}
.grid tr.row-highlight td{background:#eaff00!important;color:#111!important;border-top-color:#c8db00!important;box-shadow:inset 0 0 0 1px rgba(135,150,0,.42)!important}
.grid tr.row-highlight td.no{background:#dfff00!important;color:#111!important}
.grid tr.row-highlight td .time{background:transparent!important;color:#111!important;padding:0!important}
.grid tr.row-highlight td .ext,.grid tr.row-highlight td .ext b{color:#111!important}
.grid tr.row-highlight td .next-countdown{background:#111827!important;color:#fff!important}
.route-gap-guide{margin-top:15px;border-radius:11px;overflow:hidden;background:#000;box-shadow:0 1px 0 var(--line),0 8px 24px rgba(0,0,0,.16)}
.route-gap-grid{display:grid;grid-template-columns:1.12fr repeat(4,1fr);font-weight:900;text-align:center}
.route-gap-grid>div{display:flex;align-items:center;justify-content:center;min-width:0;padding:8px 2px;border-right:1px solid transparent;line-height:1.18}
.route-gap-grid>div:nth-child(5n){border-right:0}
.route-gap-grid .black{background:#000;color:#fff;font-size:12px;white-space:nowrap}
.route-gap-grid .station{color:#00d8ff;font-size:13px}
.route-gap-grid .yellow{background:#fff88e;color:#ff1717;border-right-color:#242424;font-size:13px;white-space:nowrap}
@media(max-width:380px){.route-gap-grid .black{font-size:10.5px}.route-gap-grid .yellow,.route-gap-grid .station{font-size:11px}.route-gap-grid>div{padding:7px 1px}}
'''
text = text.replace("</style>", css + "\n</style>", 1)

guide_html = r'''
<section class="route-gap-guide" aria-label="신논현역 주말 공휴일 운행 간격 안내">
  <div class="route-gap-grid">
    <div class="black"></div><div class="black">1번차(오전)</div><div class="black">2번차(오전)</div><div class="black">나머지차</div><div class="black">막탕(오/전후)</div>
    <div class="black station">신논현역</div><div class="black">6:05 AM'</div><div class="black">6:20 AM'</div><div class="black"></div><div class="black"></div>
    <div class="yellow">주말.공휴일</div><div class="yellow">2시간25분</div><div class="yellow">2시25분</div><div class="yellow">2시간25분</div><div class="yellow">2시간25분</div>
  </div>
</section>
'''
text = text.replace("</main>", guide_html + "\n</main>", 1)

js = r'''

/* Rev23: highlighted rows persist until the same number is tapped again. */
const rev23StorageKey="1560-row-highlights-rev22";
let rev23Highlights={};
try{
 const saved=localStorage.getItem(rev23StorageKey);
 if(saved)rev23Highlights=JSON.parse(saved)||{};
}catch(_){rev23Highlights={};}
function rev23SaveHighlights(){
 try{localStorage.setItem(rev23StorageKey,JSON.stringify(rev23Highlights));}catch(_){}
}
function rev23SelectedRows(day){
 const value=rev23Highlights[day];
 return Array.isArray(value)?value:[];
}
function rev23ApplyHighlights(){
 const selected=new Set(rev23SelectedRows(state.day).map(Number));
 [...rowsEl.children].forEach((row,index)=>row.classList.toggle("row-highlight",selected.has(index)));
}
function rev23ToggleRow(index){
 const selected=new Set(rev23SelectedRows(state.day).map(Number));
 if(selected.has(index))selected.delete(index);else selected.add(index);
 rev23Highlights[state.day]=[...selected].sort((a,b)=>a-b);
 rev23SaveHighlights();
 rev23ApplyHighlights();
}
function rev23Events(day){
 const events=[];
 DATA[day].rows.forEach((row,ri)=>{
  row.t.forEach((time,ci)=>{if(time)events.push({time,min:toMin(time),ri,ci,kind:"base"})});
  if(row.ext)events.push({time:row.ext,min:toMin(row.ext),ri,ci:4,kind:"ext"});
 });
 return events.sort((a,b)=>a.min-b.min);
}
function rev23TargetMs(event,base){
 const d=new Date(base);d.setHours(Math.floor(event.min/60),event.min%60,0,0);return d.getTime();
}
function rev23CounterNode(){
 const span=document.createElement("span");span.className="next-countdown";span.textContent="⏱ 00:00:00";return span;
}
function rev23EnsureTimeSpan(td,time){
 let span=td.querySelector(":scope > .time");
 if(span)return span;
 const first=[...td.childNodes].find(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim());
 span=document.createElement("span");span.className="time";span.textContent=time;
 if(first)td.replaceChild(span,first);else td.insertBefore(span,td.firstChild);
 return span;
}
function rev23UpdateInspectionCount(){
 const notice=document.querySelector(".notice");
 if(!notice||!DATA[state.day])return;
 let badge=notice.querySelector(".service-count");
 if(!badge){
  badge=document.createElement("span");badge.className="service-count";
  const right=notice.querySelector("b:last-child");notice.insertBefore(badge,right||null);
 }
 badge.textContent=`${DATA[state.day].count}대`;
 badge.setAttribute("aria-label",`운행대수 ${DATA[state.day].count}대`);
}
function rev23SyncCounter(){
 rev23UpdateInspectionCount();rev23ApplyHighlights();
 document.querySelectorAll(".next-countdown").forEach(el=>el.remove());
 document.querySelectorAll(".grid td.next").forEach(el=>el.classList.remove("next"));
 document.querySelectorAll(".ext.next-ext").forEach(el=>el.classList.remove("next-ext"));
 if(state.day!==todayKey())return;
 const now=new Date();const events=rev23Events(state.day);let event=null;
 for(const item of events){if(rev23TargetMs(item,now)<=now.getTime())event=item;else break;}
 if(!event)return;
 const row=rowsEl.children[event.ri],td=row&&row.children[event.ci+1];if(!td)return;
 const counter=rev23CounterNode();
 if(event.kind==="ext"){
  const ext=td.querySelector(".ext");if(!ext)return;ext.classList.add("next-ext");ext.appendChild(counter);
 }else{td.classList.add("next");rev23EnsureTimeSpan(td,event.time);td.appendChild(counter);}
 const diff=Math.max(0,Date.now()-rev23TargetMs(event,now));
 const total=Math.floor(diff/1000),h=Math.floor(total/3600),m=Math.floor((total%3600)/60),s=total%60,p=n=>String(n).padStart(2,"0");
 counter.textContent=`⏱ ${p(h)}:${p(m)}:${p(s)}`;
 counter.setAttribute("aria-label",`출발 후 ${h}시간 ${m}분 ${s}초 경과`);
 rev23ApplyHighlights();
}
rowsEl.addEventListener("click",event=>{
 const numberCell=event.target.closest("td.no");if(!numberCell||!rowsEl.contains(numberCell))return;
 const row=numberCell.closest("tr"),index=[...rowsEl.children].indexOf(row);if(index>=0)rev23ToggleRow(index);
});
const rev23Observer=new MutationObserver(()=>rev23ApplyHighlights());
rev23Observer.observe(rowsEl,{childList:true});
setInterval(rev23SyncCounter,1000);setTimeout(rev23SyncCounter,0);
'''
pos = text.rfind("</script>")
if pos == -1:
    raise RuntimeError("index.html script closing tag not found")
text = text[:pos] + js + "\n" + text[pos:]

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev23-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
