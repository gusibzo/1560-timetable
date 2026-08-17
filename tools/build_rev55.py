from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev54.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.54", "Rev.55")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=54",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=55",{updateViaCache:"none"})',
    1,
)

# Rev55: color only the A/B suffix on the front route sign.
# 1560 stays red/orange, A is green, B is yellow. Keep the Rev54 schedule logic,
# Rev53 LED headlights, Rev52 firefly glow and elapsed-time badge unchanged.
css = r'''
/* Rev55: real-bus-inspired two-color front route sign. */
body .grid tbody td.next > .time{
  position:relative!important;
}
body .grid tbody td.next > .time::before{
  content:""!important;
  display:none!important;
}
body .grid tbody td.next > .time > .rev55-route-sign{
  position:absolute!important;
  z-index:7!important;
  left:13px!important;
  right:13px!important;
  top:6px!important;
  height:9px!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  gap:1px!important;
  border:1px solid rgba(91,104,111,.68)!important;
  border-radius:2px!important;
  background:#11161b!important;
  font:900 6.5px/1 ui-monospace,SFMono-Regular,Menlo,monospace!important;
  letter-spacing:.65px!important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.04)!important;
  pointer-events:none!important;
  white-space:nowrap!important;
}
body .grid tbody td.next > .time > .rev55-route-sign .route-num{
  color:#ff4b42!important;
  text-shadow:0 0 3px rgba(255,75,66,.88)!important;
}
body .grid tbody td.next > .time > .rev55-route-sign .route-letter{
  font-weight:950!important;
}
body .grid tbody td.next > .time > .rev55-route-sign .route-letter.route-a{
  color:#48ef72!important;
  text-shadow:0 0 3px rgba(72,239,114,.95),0 0 5px rgba(72,239,114,.55)!important;
}
body .grid tbody td.next > .time > .rev55-route-sign .route-letter.route-b{
  color:#ffd84d!important;
  text-shadow:0 0 3px rgba(255,216,77,.95),0 0 5px rgba(255,216,77,.55)!important;
}
@media(max-width:380px){
  body .grid tbody td.next > .time > .rev55-route-sign{
    left:12px!important;right:12px!important;font-size:6.2px!important;
  }
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev55: 1560 is red, A is green (trip 1/2), B is yellow (trip 3/4/5). */
function rev55SyncFrontSignColors(){
  document.querySelectorAll(".grid tbody td.next > .time").forEach(time=>{
    const td=time.closest("td");
    if(!td)return;
    const tripNo=td.cellIndex;
    const letter=tripNo<=2?"A":"B";
    const cls=letter==="A"?"route-a":"route-b";
    const route=`1560${letter}`;
    time.dataset.route=route;
    let sign=time.querySelector(":scope > .rev55-route-sign");
    if(!sign){
      sign=document.createElement("span");
      sign.className="rev55-route-sign";
      sign.setAttribute("aria-hidden","true");
      time.appendChild(sign);
    }
    if(sign.dataset.letter!==letter){
      sign.dataset.letter=letter;
      sign.innerHTML=`<span class="route-num">1560</span><span class="route-letter ${cls}">${letter}</span>`;
    }
    const visibleTime=[...time.childNodes].find(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim());
    const labelTime=visibleTime?visibleTime.textContent.trim():"현재 운행";
    time.setAttribute("aria-label",`${labelTime} ${route}`);
  });
}
setInterval(rev55SyncFrontSignColors,400);
setTimeout(rev55SyncFrontSignColors,100);
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev55-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="55";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
