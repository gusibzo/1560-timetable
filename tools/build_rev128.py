from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev127.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.127", "Rev.128")

registration = 'navigator.serviceWorker.register("./sw.js?v=127",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev127 service worker registration is missing")
text = text.replace(registration, registration.replace("v=127", "v=128"), 1)

# Rev124 temporarily replaced the 2026 Chuseok public-holiday timetable with
# an incorrect five-bus schedule. The confirmed 9/24 assignment sheet matches
# the existing autumn public-holiday timetable (8 buses) exactly, so remove
# that override and let the normal Sunday/public-holiday data render.
text, removed = re.subn(
    r'\n/\* Rev124: temporary five-bus timetable for the four-day 2026 Chuseok holiday\. \*/.*?\nif\(rev124TodayIsFiveBus\)\{.*?\n\}\n',
    "\n",
    text,
    count=1,
    flags=re.S,
)
if removed != 1:
    raise RuntimeError("Rev124 five-bus override is missing")

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev128-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="128";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
