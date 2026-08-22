from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev65.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.65", "Rev.66")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=65",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=66",{updateViaCache:"none"})',
    1,
)

# Rev66: remove the elapsed-time badge under the live bus cursor completely.
# Also restore the cursor's departure time to bright white when the same row is
# fluorescent-highlighted; Rev64 intentionally made normal highlighted-row
# times dark, which also affected the live .next cursor.
css = r'''
/* Rev66: no elapsed timer badge under the live cursor. */
.next-countdown{
  display:none!important;
}

/* Rev66: the time inside the live bus cursor must stay clearly readable. */
body .grid tbody tr.rev63-row-selected td.next > .time,
body .grid tbody td.next > .time{
  color:#fff!important;
  text-shadow:
    0 1px 1px rgba(0,0,0,.95),
    0 0 3px rgba(0,0,0,.92),
    0 0 6px rgba(0,0,0,.72)!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev66: continuously remove old/new elapsed-counter helpers from the DOM. */
function rev66RemoveElapsedCounters(){
  document.querySelectorAll(".next-countdown").forEach(el=>el.remove());
}
setTimeout(rev66RemoveElapsedCounters,50);
setInterval(rev66RemoveElapsedCounters,250);
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev66-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="66";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
