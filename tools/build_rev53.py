from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev52.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.52", "Rev.53")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=52",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=53",{updateViaCache:"none"})',
    1,
)

# Rev53: change the current-trip bus headlights from round lamps to tall LED
# clusters like the reference vehicle, and show 1560A for trip 1/2 and
# 1560B for trip 3/4/5. Keep Rev52 firefly glow and elapsed-time badge.
css = r'''
/* Rev53: vertical LED headlights + dynamic A/B front route sign. */
body .grid tbody td.next > .time{
  background:
    radial-gradient(ellipse 5px 14px at 13% 81%,
      #ffffff 0 22%,
      #dff8ff 24% 38%,
      #9fd6e8 40% 49%,
      #586b75 51% 60%,
      #232a30 62% 72%,
      transparent 74%),
    radial-gradient(ellipse 5px 14px at 87% 81%,
      #ffffff 0 22%,
      #dff8ff 24% 38%,
      #9fd6e8 40% 49%,
      #586b75 51% 60%,
      #232a30 62% 72%,
      transparent 74%),
    radial-gradient(ellipse 2px 9px at 12.5% 78%,rgba(255,255,255,.96) 0 40%,transparent 44%),
    radial-gradient(ellipse 2px 9px at 87.5% 78%,rgba(255,255,255,.96) 0 40%,transparent 44%),
    linear-gradient(180deg,
      #ee3b37 0 18%,
      #151a20 18% 61%,
      #de302e 61% 72%,
      #c9cdd1 72% 91%,
      #24282d 91% 100%)!important;
}
body .grid tbody td.next > .time::before{
  content:attr(data-route)!important;
  color:#ff4b42!important;
  letter-spacing:.65px!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

js = r'''

/* Rev53: front sign follows trip column: 1/2=A, 3/4/5=B. */
function rev53SyncFrontSign(){
  const td=document.querySelector(".grid tbody td.next");
  if(!td)return;
  const time=td.querySelector(":scope > .time");
  if(!time)return;
  const tripNo=td.cellIndex; // first timetable cell is trip 1; cellIndex is 1..5 after the No. cell
  time.dataset.route=(tripNo<=2)?"1560A":"1560B";
  time.setAttribute("aria-label",`${time.textContent} ${time.dataset.route}`);
}
setInterval(rev53SyncFrontSign,400);
setTimeout(rev53SyncFrontSign,80);
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
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev53-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="53";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
