from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev89.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.89", "Rev.90")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=89",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=90",{updateViaCache:"none"})',
    1,
)

# Clarify that Monday is the fixed inspection day, not today's weekday.
old_notice = '<div class="notice"><span>검차</span><b>월요일</b></div>'
new_notice = '<div class="notice"><span>검차일</span><b>매주 월요일</b></div>'
if text.count(old_notice) != 1:
    raise RuntimeError("Rev89 inspection notice was not found exactly once")
text = text.replace(old_notice, new_notice, 1)

rev90_script = '''

/* Rev90: keep the selected schedule aligned with the real calendar day. */
function rev90DateStamp(){
  const n=new Date(),p=v=>String(v).padStart(2,"0");
  return `${n.getFullYear()}-${p(n.getMonth()+1)}-${p(n.getDate())}`;
}
let rev90KnownDate=rev90DateStamp();
function rev90MarkTodayTab(){
  const current=todayKey();
  document.querySelectorAll(".seg").forEach(btn=>{
    const count=btn.querySelector(".cnt");
    if(!count||!DATA[btn.dataset.day])return;
    const buses=`${DATA[btn.dataset.day].count}대`;
    count.textContent=btn.dataset.day===current?`오늘 · ${buses}`:buses;
    btn.setAttribute("aria-label",`${DATA[btn.dataset.day].label} 시간표${btn.dataset.day===current?" · 오늘":""}`);
  });
}
function rev90SelectToday(force){
  const stamp=rev90DateStamp();
  if(force||stamp!==rev90KnownDate){
    rev90KnownDate=stamp;
    state.day=todayKey();
    render();
  }
  rev90MarkTodayTab();
}
document.addEventListener("visibilitychange",()=>{if(!document.hidden)rev90SelectToday(true)});
window.addEventListener("pageshow",()=>rev90SelectToday(true));
setInterval(()=>rev90SelectToday(false),30000);
setTimeout(()=>rev90SelectToday(true),0);
'''
if "</body>" not in text:
    raise RuntimeError("Document body is missing")
text = text.replace("</body>", "<script>" + rev90_script + "</script>\n</body>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev90-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="90";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
