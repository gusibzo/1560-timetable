from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev126.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.126", "Rev.127")

registration = 'navigator.serviceWorker.register("./sw.js?v=126",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev126 service worker registration is missing")
text = text.replace(registration, registration.replace("v=126", "v=127"), 1)

# Rev125 opened road-traffic links in a new Android browser tab. Some CCTV
# viewers leave that tab at a temporary content://media URL, which later shows
# ERR_FILE_NOT_FOUND. Keep navigation in the current tab so Back returns to the
# timetable instead of reopening a stale media URI.
pattern = re.compile(r'(<a class="traffic-choice [^"]+"[^>]*?) target="_blank"([^>]*>)')
text, changed = pattern.subn(r"\1\2", text)
if changed != 5:
    raise RuntimeError(f"Expected 5 road-traffic links, changed {changed}")

# Close the chooser whenever the page becomes visible again after returning
# from a CCTV or map page.
anchor = '  window.addEventListener("pageshow",function(){modal.classList.remove("open")});'
replacement = anchor + '\n  document.addEventListener("visibilitychange",function(){if(!document.hidden)modal.classList.remove("open")});'
if text.count(anchor) != 1:
    raise RuntimeError("Traffic modal pageshow handler is missing")
text = text.replace(anchor, replacement, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev127-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="127";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
