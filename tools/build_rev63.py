from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev62.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.62", "Rev.63")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=62",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=63",{updateViaCache:"none"})',
    1,
)

# Rev63: controls are real push-buttons, not switch/toggle-looking controls.
# The timetable's left 순번 column becomes the 1~13 vertical bus selector.
css = r'''
/* Rev63: push-button calendar entry + vertical bus-number buttons. */
.rev58-today-work,
.rev58-today-work.checked{
  position:relative!important;
  width:100%!important;
  min-height:44px!important;
  margin-top:8px!important;
  padding:10px 14px!important;
  border:1px solid rgba(255,255,255,.16)!important;
  border-radius:12px!important;
  background:linear-gradient(180deg,#3d4652,#2d3540)!important;
  color:#fff!important;
  box-shadow:0 2px 0 rgba(0,0,0,.34),inset 0 1px 0 rgba(255,255,255,.12)!important;
  font:950 12px/1.25 inherit!important;
  cursor:pointer!important;
}
.rev58-today-work:active{
  transform:translateY(1px)!important;
  box-shadow:0 1px 0 rgba(0,0,0,.30),inset 0 1px 0 rgba(255,255,255,.08)!important;
}
.grid td.no{
  padding:6px 4px!important;
  background:transparent!important;
}
.grid tr:nth-child(even) td.no{
  background:transparent!important;
}
.rev63-row-btn{
  -webkit-appearance:none;
  appearance:none;
  touch-action:manipulation;
  width:46px;
  height:38px;
  max-width:calc(100% - 2px);
  border:1px solid #aeb6c0;
  border-radius:12px;
  background:linear-gradient(180deg,#f9fafb,#e6eaf0);
  color:#177226;
  font:950 15px/1 inherit;
  font-variant-numeric:tabular-nums;
  box-shadow:0 2px 4px rgba(0,0,0,.13),inset 0 1px 0 rgba(255,255,255,.95);
  cursor:pointer;
}
.rev63-row-btn:active{
  transform:translateY(1px);
  box-shadow:0 1px 2px rgba(0,0,0,.12),inset 0 1px 0 rgba(255,255,255,.75);
}
.rev63-row-btn[aria-pressed="true"]{
  border-color:#e23b2e;
  background:linear-gradient(180deg,#ff5a4e,#e23b2e);
  color:#fff;
  box-shadow:0 0 0 2px rgba(226,59,46,.18),0 2px 5px rgba(0,0,0,.18),inset 0 1px 0 rgba(255,255,255,.28);
}
.grid tr.rev63-row-selected td:not(.no){
  box-shadow:inset 0 2px 0 rgba(226,59,46,.20),inset 0 -2px 0 rgba(226,59,46,.20);
}
@media(max-width:360px){
  .rev63-row-btn{width:42px;height:36px;font-size:14px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev63: use the existing left 순번 cells as the vertical 1~13 selector. */
const rev63BusKey="1560-selected-bus-v1";
function rev63SelectedBus(){
  try{return localStorage.getItem(rev63BusKey)||"";}catch(_){return "";}
}
function rev63SetSelectedBus(value){
  try{
    if(value)localStorage.setItem(rev63BusKey,value);
    else localStorage.removeItem(rev63BusKey);
  }catch(_){}
}
function rev63EnhanceRowButtons(){
  const selected=rev63SelectedBus();
  document.querySelectorAll(".grid tbody td.no").forEach(td=>{
    let btn=td.querySelector(":scope > .rev63-row-btn");
    if(!btn){
      const raw=(td.textContent||"").trim();
      const m=raw.match(/\d+/);
      if(!m)return;
      const no=m[0];
      td.textContent="";
      btn=document.createElement("button");
      btn.type="button";
      btn.className="rev63-row-btn";
      btn.dataset.busNo=no;
      btn.textContent=no;
      btn.setAttribute("aria-label",`${no}번 선택`);
      btn.addEventListener("click",ev=>{
        ev.preventDefault();
        ev.stopPropagation();
        const current=rev63SelectedBus();
        rev63SetSelectedBus(current===no?"":no);
        rev63EnhanceRowButtons();
      });
      td.appendChild(btn);
    }
    const no=btn.dataset.busNo||btn.textContent.trim();
    const active=!!selected&&selected===no;
    btn.setAttribute("aria-pressed",active?"true":"false");
    btn.setAttribute("aria-label",active?`${no}번 선택됨`:`${no}번 선택`);
    const tr=td.closest("tr");
    if(tr)tr.classList.toggle("rev63-row-selected",active);
  });
}
function rev63RefreshCalendarButton(){
  const btn=document.getElementById("rev58-today-work");
  if(!btn)return;
  const today=new Date();
  const count=typeof rev58MonthCount==="function"?rev58MonthCount(today.getFullYear(),today.getMonth()):0;
  btn.classList.remove("checked");
  btn.setAttribute("aria-pressed","false");
  btn.textContent=`📅 근무일 달력 열기 · 8/17부터 · 이번 달 ${count}일`;
}
setInterval(()=>{rev63EnhanceRowButtons();rev63RefreshCalendarButton();},700);
setTimeout(()=>{rev63EnhanceRowButtons();rev63RefreshCalendarButton();},120);
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev63-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="63";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
