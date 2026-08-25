from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev73.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.73", "Rev.74")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=73",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=74",{updateViaCache:"none"})',
    1,
)

# Rev74: put current trip, elapsed counter, and next departure on one horizontal row.
# The elapsed counter gets the center column so the whole briefing is easier to scan.
old_cards = '''      <div class="rev57-briefing-item"><span class="rev57-briefing-k">출발 카운터</span><strong id="rev57-current" class="rev57-briefing-v">—</strong></div>
      <div class="rev57-briefing-item"><span class="rev57-briefing-k">다음 출발</span><strong id="rev57-next" class="rev57-briefing-v">—</strong></div>'''
new_cards = '''      <div class="rev57-briefing-item rev74-current-card"><span class="rev57-briefing-k">현재 출발</span><strong id="rev57-current" class="rev57-briefing-v">—</strong></div>
      <div class="rev57-briefing-item rev74-counter-card"><span class="rev57-briefing-k">카운터</span><strong id="rev74-counter" class="rev74-counter">00:00:00</strong></div>
      <div class="rev57-briefing-item rev74-next-card"><span class="rev57-briefing-k">다음 출발</span><strong id="rev57-next" class="rev57-briefing-v">—</strong></div>'''
if old_cards not in text:
    raise RuntimeError("Rev73 briefing cards not found")
text = text.replace(old_cards, new_cards, 1)

text = text.replace(
    'const currentEl=document.getElementById("rev57-current");\n  const nextEl=document.getElementById("rev57-next");',
    'const currentEl=document.getElementById("rev57-current");\n  const counterEl=document.getElementById("rev74-counter");\n  const nextEl=document.getElementById("rev57-next");',
    1,
)

old_current = '''if(currentEl){
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
new_current = '''if(currentEl){
    if(current){
      const elapsed=Math.max(0,Math.floor((nowMin-current.min)*60));
      const hh=String(Math.floor(elapsed/3600)).padStart(2,"0");
      const mm=String(Math.floor((elapsed%3600)/60)).padStart(2,"0");
      const ss=String(elapsed%60).padStart(2,"0");
      currentEl.textContent=current.kind==="ext"
        ? `${current.ri+1}번 · 추가`
        : `${current.ri+1}번 · ${current.ci+1}회`;
      if(counterEl)counterEl.textContent=`${hh}:${mm}:${ss}`;
    }else{
      currentEl.textContent="운행 전";
      if(counterEl)counterEl.textContent="00:00:00";
    }
  }'''
if old_current not in text:
    raise RuntimeError("Rev72 current counter block not found")
text = text.replace(old_current, new_current, 1)

css = r'''
/* Rev74: current | counter | next, all on one horizontal row. */
.rev57-briefing-grid{
  grid-template-columns:minmax(0,.86fr) minmax(118px,1.08fr) minmax(0,1.06fr)!important;
  gap:6px!important;
}
.rev57-briefing-item{
  min-height:76px!important;
  display:flex!important;
  flex-direction:column!important;
  justify-content:center!important;
  padding:8px 7px!important;
}
.rev74-current-card,
.rev74-next-card{
  text-align:left!important;
}
.rev74-counter-card{
  align-items:center!important;
  text-align:center!important;
}
#rev57-current{
  display:block!important;
  margin-top:5px!important;
  color:#baff64!important;
  font-size:12px!important;
  line-height:1.15!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
}
.rev74-counter{
  display:block!important;
  width:100%!important;
  margin-top:5px!important;
  color:#fff!important;
  font:950 22px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace!important;
  letter-spacing:-1px!important;
  font-variant-numeric:tabular-nums!important;
  white-space:nowrap!important;
  text-align:center!important;
  text-shadow:0 1px 1px rgba(0,0,0,.82),0 0 7px rgba(186,255,100,.18)!important;
}
#rev57-next{
  margin-top:5px!important;
  font-size:11.5px!important;
  line-height:1.15!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
}
.rev72-current-trip,.rev72-counter,.rev72-before{display:none!important}
@media(max-width:380px){
  .rev57-briefing-grid{grid-template-columns:minmax(0,.8fr) minmax(106px,1.05fr) minmax(0,1.05fr)!important;gap:5px!important}
  .rev57-briefing-item{padding:7px 5px!important;min-height:72px!important}
  #rev57-current{font-size:10.5px!important}
  .rev74-counter{font-size:20px!important;letter-spacing:-1.2px!important}
  #rev57-next{font-size:10.5px!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev74-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="74";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
