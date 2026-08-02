from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev40.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.40", "Rev.41")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=40",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=41",{updateViaCache:"none"})',
    1,
)

css = r'''
/* Rev41: highlight 5:00, 12:00, 11:30 and 22:30 with light pink and bold black text. */
.grid tbody td.special-time-pink,
.grid tbody tr:nth-child(even) td.special-time-pink,
body[data-day="sunday"] .grid tbody td.special-time-pink,
body[data-day="sunday"] .grid tbody td.special-time-pink.edge{
  background:#f8cddd!important;
  color:#111!important;
  border-top-color:#e4a8bd!important;
  font-weight:950!important;
  text-shadow:none!important;
  box-shadow:inset 0 0 0 1px rgba(205,92,137,.24)!important;
}
.grid tbody td.special-time-pink .time,
.grid tbody td.special-time-pink .ext,
.grid tbody td.special-time-pink .ext b{
  background:transparent!important;
  color:#111!important;
  font-weight:950!important;
  text-shadow:none!important;
}
.grid tbody td.special-time-pink .time{
  padding:0!important;
  border-radius:0!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

script = r'''
<script>
(function(){
  const pinkTimes = new Set(["5:00", "12:00", "11:30", "22:30"]);

  function markPinkTimes(){
    document.querySelectorAll(".grid tbody td").forEach(function(td){
      td.classList.remove("special-time-pink");
      if(td.classList.contains("no") || td.classList.contains("blank")) return;

      const timeNode = td.querySelector(".time");
      const source = (timeNode ? timeNode.textContent : td.textContent).trim();
      const match = source.match(/^([0-2]?\d:\d{2})/);
      if(match && pinkTimes.has(match[1])){
        td.classList.add("special-time-pink");
      }
    });
  }

  function startPinkTimeWatcher(){
    markPinkTimes();
    requestAnimationFrame(markPinkTimes);
    setTimeout(markPinkTimes, 120);

    const grid = document.querySelector(".grid");
    if(grid){
      new MutationObserver(markPinkTimes).observe(grid, {
        childList:true,
        subtree:true,
        characterData:true
      });
    }

    document.addEventListener("click", function(event){
      if(event.target.closest(".seg")){
        requestAnimationFrame(markPinkTimes);
        setTimeout(markPinkTimes, 80);
      }
    });
  }

  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", startPinkTimeWatcher, {once:true});
  }else{
    startPinkTimeWatcher();
  }
  window.addEventListener("pageshow", markPinkTimes);
})();
</script>
'''
if "</body>" not in text:
    raise RuntimeError("Closing body tag was not found")
text = text.replace("</body>", script + "\n</body>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev41-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="41";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
