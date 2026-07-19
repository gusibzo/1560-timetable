from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
index = root / "index.html"
text = index.read_text(encoding="utf-8")

# Revision and the Rev.18 labels/calendar requested by the user.
text = re.sub(r"Rev\.1[78]", "Rev.19", text)
for old, new in {
    '일요일<span class="cnt">8대</span>': '일요일(공휴일)<span class="cnt">8대</span>',
    'sunday:{label:"일요일",count:8': 'sunday:{label:"일요일(공휴일)",count:8',
    '대한민국 음력·공휴일 달력': '대한민국 달력',
    '음력 · 공휴일 · 대체공휴일 · 주요 전통일 표시': '음력 · 공휴일 · 주요 전통일 표시',
}.items():
    text = text.replace(old, new)

# Kakao Map -> official TMAP web route page.
text = text.replace(
    '.gps-actions .kakao{background:#fae100;color:#2d2000}',
    '.gps-actions .tmap{background:#111827;color:#fff}',
)
text = text.replace(
    '<a class="kakao" href="https://m.map.kakao.com/" target="_blank" rel="noopener noreferrer">🧭 카카오맵</a>',
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" target="_blank" rel="noopener noreferrer">🧭 T맵</a>',
)
text = text.replace(
    '<a class="naver" href="https://map.kakao.com/link/to/현재위치,37.5665,126.9780" target="_blank" rel="noopener noreferrer">🚏 길찾기 예시</a>',
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" target="_blank" rel="noopener noreferrer">🚏 T맵 길찾기</a>',
)

css_marker = "/* Rev19: Sunday summary and live departure counter */"
if css_marker not in text:
    css = r'''
/* Rev19: Sunday summary and live departure counter */
.seg[data-day="sunday"]{font-size:12px;letter-spacing:-.5px}
body[data-day="sunday"] .chips .chip:nth-child(1),body[data-day="sunday"] .chips .chip:nth-child(2){background:var(--brand);box-shadow:0 1px 0 #b5271f,inset 0 1px 0 rgba(255,255,255,.18)}
body[data-day="sunday"] .chips .chip:nth-child(1) .k,body[data-day="sunday"] .chips .chip:nth-child(2) .k,body[data-day="sunday"] .chips .chip:nth-child(1) .v,body[data-day="sunday"] .chips .chip:nth-child(2) .v{color:#fff!important}
.next-countdown{display:block;width:max-content;max-width:100%;margin:4px auto 0;padding:2px 4px;border-radius:6px;background:#111827;color:#fff;font-size:8.5px;font-weight:950;line-height:1.15;white-space:nowrap;letter-spacing:-.2px}
.ext.next-ext{margin:4px auto 0;padding:3px 2px;border-radius:7px;background:var(--accent);color:#fff!important}
.ext.next-ext b{color:#fff!important}
.ext.next-ext .next-countdown{margin-top:3px;background:#fff;color:#111827}
'''
    text = text.replace("</style>", css + "\n</style>", 1)

js_marker = "/* Rev19 live countdown */"
if js_marker not in text:
    js = r'''

/* Rev19 live countdown */
function rev19Events(day){
 const events=[];
 DATA[day].rows.forEach((row,ri)=>{
  row.t.forEach((time,ci)=>{if(time)events.push({time,min:toMin(time),ri,ci,kind:"base"})});
  if(row.ext)events.push({time:row.ext,min:toMin(row.ext),ri,ci:4,kind:"ext"});
 });
 return events.sort((a,b)=>a.min-b.min);
}
function rev19TargetMs(event,base){
 const d=new Date(base);d.setHours(Math.floor(event.min/60),event.min%60,0,0);return d.getTime();
}
function rev19CountdownNode(){
 const span=document.createElement("span");span.className="next-countdown";span.textContent="⏱ --:--:--";return span;
}
function rev19EnsureTimeSpan(td,time){
 let span=td.querySelector(":scope > .time");
 if(span)return span;
 const first=[...td.childNodes].find(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim());
 span=document.createElement("span");span.className="time";span.textContent=time;
 if(first)td.replaceChild(span,first);else td.insertBefore(span,td.firstChild);
 return span;
}
function rev19SyncCounter(){
 document.querySelectorAll(".next-countdown").forEach(el=>el.remove());
 document.querySelectorAll(".grid td.next").forEach(el=>el.classList.remove("next"));
 document.querySelectorAll(".ext.next-ext").forEach(el=>el.classList.remove("next-ext"));
 if(state.day!==todayKey())return;
 const now=new Date();
 const event=rev19Events(state.day).find(e=>rev19TargetMs(e,now)>=now.getTime());
 if(!event)return;
 const row=rowsEl.children[event.ri],td=row&&row.children[event.ci+1];
 if(!td)return;
 const counter=rev19CountdownNode();
 if(event.kind==="ext"){
  const ext=td.querySelector(".ext");if(!ext)return;ext.classList.add("next-ext");ext.appendChild(counter);
 }else{
  td.classList.add("next");rev19EnsureTimeSpan(td,event.time);td.appendChild(counter);
 }
 const diff=Math.max(0,rev19TargetMs(event,now)-Date.now());
 const total=Math.ceil(diff/1000),h=Math.floor(total/3600),m=Math.floor((total%3600)/60),s=total%60,p=n=>String(n).padStart(2,"0");
 counter.textContent=`⏱ ${p(h)}:${p(m)}:${p(s)}`;
 counter.setAttribute("aria-label",`출발까지 ${h}시간 ${m}분 ${s}초`);
}
setInterval(rev19SyncCounter,1000);
setTimeout(rev19SyncCounter,0);
'''
    pos = text.rfind("</script>")
    if pos == -1:
        raise RuntimeError("index.html script closing tag not found")
    text = text[:pos] + js + "\n" + text[pos:]

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev19-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
