from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev58.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.58", "Rev.59")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=58",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=59",{updateViaCache:"none"})',
    1,
)

# Rev59: "remaining departures" means only the regular timetable departures.
# Do not count the separate +Gangnam extension departures in this number.
old_remaining = 'const remaining=events.filter(ev=>ev.min>nowMin).length;'
new_remaining = 'const remaining=events.filter(ev=>ev.kind==="base"&&ev.min>nowMin).length;'
if old_remaining not in text:
    raise RuntimeError("Rev57 remaining-departure counter definition not found")
text = text.replace(old_remaining, new_remaining, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev59-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="59";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
