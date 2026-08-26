from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev75.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.77", "Rev.78")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=77",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=78",{updateViaCache:"none"})',
    1,
)

# Rev78: show the scheduled time in the left "current departure" card.
old_current = '''currentEl.textContent=current.kind==="ext"
        ? `${current.ri+1}번 · 추가`
        : `${current.ri+1}번 · ${current.ci+1}회`;'''
new_current = '''currentEl.textContent=current.kind==="ext"
        ? `${current.ri+1}번 · 추가 ${current.time}`
        : `${current.ri+1}번 · ${current.ci+1}회 ${current.time}`;'''
if old_current not in text:
    raise RuntimeError("Rev77 current-departure block not found")
text = text.replace(old_current, new_current, 1)

# Rev78: keep the requested image button in the actual quick-link row.
# This avoids relying on which matching "Gyeonggi Bus" label appears first.
ensure_script = r'''
<script>
(function(){
  function placeRev78Photo(){
    const thumb=document.getElementById("rev77-photo-thumb");
    const bar=document.querySelector(".info-bar");
    if(!thumb||!bar)return;
    const old=[...bar.querySelectorAll("a,button")].find(el=>el!==thumb&&(el.textContent||"").includes("경기버스"));
    if(old)old.remove();
    if(thumb.parentElement!==bar)bar.appendChild(thumb);
    thumb.hidden=false;
    thumb.style.display="flex";
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",placeRev78Photo,{once:true});
  else placeRev78Photo();
  setTimeout(placeRev78Photo,300);
})();
</script>
'''
text = text.replace("</body>", ensure_script + "\n</body>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev78-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="78";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
