from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev69.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.71", "Rev.72")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=71",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=72",{updateViaCache:"none"})',
    1,
)

# Rev72: turn the left briefing card into a live elapsed-time counter.
# At each scheduled departure, the counter resets to 00:00:00 while the
# right-hand card continues to show the next departure from the timetable.
text = text.replace(
    '<span class="rev57-briefing-k">현재 출발</span>',
    '<span class="rev57-briefing-k">출발 카운터</span>',
    1,
)

old_current_update = 'if(currentEl)currentEl.textContent=current?rev57EventText(current):"운행 전";'
new_current_update = '''if(currentEl){
    if(current){
      const elapsed=Math.max(0,Math.floor((nowMin-current.min)*60));
      const hh=String(Math.floor(elapsed/3600)).padStart(2,"0");
      const mm=String(Math.floor((elapsed%3600)/60)).padStart(2,"0");
      const ss=String(elapsed%60).padStart(2,"0");
      const trip=current.kind==="ext"
        ? `${current.ri+1}번 · 추가 출발중`
        : `${current.ri+1}번 · ${current.ci+1}회 출발중`;
      currentEl.innerHTML=`<span class="rev72-current-trip">${trip}</span><span class="rev72-counter">${hh}:${mm}:${ss}</span>`;
    }else{
      currentEl.innerHTML='<span class="rev72-before">운행 전</span>';
    }
  }'''
if old_current_update not in text:
    raise RuntimeError("Rev57 current briefing update line not found")
text = text.replace(old_current_update, new_current_update, 1)

css = r'''
/* Rev72: large elapsed counter in the left briefing card. */
#rev57-current{
  display:flex!important;
  flex-direction:column!important;
  align-items:flex-start!important;
  gap:4px!important;
  overflow:visible!important;
}
.rev72-current-trip{
  display:block;
  color:#baff64;
  font-size:11px;
  font-weight:950;
  line-height:1.15;
  letter-spacing:-.25px;
  white-space:nowrap;
}
.rev72-counter{
  display:block;
  color:#fff;
  font:950 28px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  letter-spacing:-1.1px;
  font-variant-numeric:tabular-nums;
  white-space:nowrap;
  text-shadow:0 1px 1px rgba(0,0,0,.8),0 0 7px rgba(186,255,100,.18);
}
.rev72-before{
  color:#baff64;
  font-size:13px;
  font-weight:950;
}
#rev57-next{
  font-size:14px!important;
  line-height:1.25!important;
}
@media(max-width:360px){
  .rev72-current-trip{font-size:10px}
  .rev72-counter{font-size:24px;letter-spacing:-1px}
  #rev57-next{font-size:12.5px!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev72-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="72";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
