from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev64.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.64", "Rev.65")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=64",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=65",{updateViaCache:"none"})',
    1,
)

# Rev65: Rev23 had an older multi-row highlight feature that persisted every
# tapped row in localStorage and re-applied those .row-highlight classes every
# second. Rev63 introduced the new single bus selector, so the legacy feature
# must be retired completely; otherwise old fluorescent rows remain alongside
# the newly selected row.
js = r'''

/* Rev65: remove the legacy multi-row fluorescent highlights permanently. */
function rev65ClearLegacyHighlights(){
  try{localStorage.removeItem("1560-row-highlights-rev22");}catch(_){}
  try{rev23Highlights={};}catch(_){}
  document.querySelectorAll(".grid tbody tr.row-highlight").forEach(row=>row.classList.remove("row-highlight"));
}

/* Rev23's timer calls this every second; replace it with cleanup only. */
try{
  rev23ApplyHighlights=function(){
    document.querySelectorAll(".grid tbody tr.row-highlight").forEach(row=>row.classList.remove("row-highlight"));
  };
  rev23ToggleRow=function(){
    rev65ClearLegacyHighlights();
  };
}catch(_){}

rev65ClearLegacyHighlights();
setTimeout(rev65ClearLegacyHighlights,80);
setInterval(rev65ClearLegacyHighlights,500);

const rev65LegacyObserver=new MutationObserver(()=>{
  document.querySelectorAll(".grid tbody tr.row-highlight").forEach(row=>row.classList.remove("row-highlight"));
});
rev65LegacyObserver.observe(rowsEl,{childList:true,subtree:true,attributes:true,attributeFilter:["class"]});
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev65-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="65";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
