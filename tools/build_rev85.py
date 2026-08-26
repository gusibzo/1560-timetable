from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev84.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.84", "Rev.85")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=84",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=85",{updateViaCache:"none"})',
    1,
)

# Rev85: keep current/next times tied to the selected bus, but restore the
# center counter to elapsed time since that bus's current departure.
old_counter = '''  const countdown=next?Math.max(0,Math.ceil((next.min-nowMin)*60)):0;
  const hh=String(Math.floor(countdown/3600)).padStart(2,"0");
  const mm=String(Math.floor((countdown%3600)/60)).padStart(2,"0");
  const ss=String(countdown%60).padStart(2,"0");
  if(currentEl)currentEl.textContent=current?current.time:"운행 전";
  if(counterEl)counterEl.textContent=`${hh}:${mm}:${ss}`;'''
new_counter = '''  const elapsed=current?Math.max(0,Math.floor((nowMin-current.min)*60)):0;
  const hh=String(Math.floor(elapsed/3600)).padStart(2,"0");
  const mm=String(Math.floor((elapsed%3600)/60)).padStart(2,"0");
  const ss=String(elapsed%60).padStart(2,"0");
  if(currentEl)currentEl.textContent=current?current.time:"운행 전";
  if(counterEl)counterEl.textContent=`${hh}:${mm}:${ss}`;'''
if text.count(old_counter) != 1:
    raise RuntimeError("Rev84 countdown block was not found exactly once")
text = text.replace(old_counter, new_counter, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev85-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="85";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
