from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev55.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.55", "Rev.56")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=55",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=56",{updateViaCache:"none"})',
    1,
)

# Rev56: when the current-trip cursor advances, the old .time span remains in
# the table. Rev55's route-sign child remained inside it and became plain text
# after the td lost .next. Hide every stale route-sign globally and only allow
# the existing high-specificity Rev55 rule to display the sign inside td.next.
css = r'''
/* Rev56: never let an old 1560A/1560B sign leak into a timetable cell. */
.rev55-route-sign{display:none!important;}
body .grid tbody td.next > .time > .rev55-route-sign{display:flex!important;}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev56: remove stale route-sign nodes left behind when the cursor moves. */
function rev56CleanStaleRouteSigns(){
  document.querySelectorAll(".grid tbody td:not(.next) .rev55-route-sign").forEach(el=>el.remove());
  document.querySelectorAll(".grid tbody td").forEach(td=>{
    [...td.childNodes].forEach(node=>{
      if(node.nodeType===Node.TEXT_NODE && /^1560[AB]$/.test(node.textContent.trim()))node.remove();
    });
  });
}
setInterval(rev56CleanStaleRouteSigns,250);
setTimeout(rev56CleanStaleRouteSigns,0);
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev56-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="56";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
