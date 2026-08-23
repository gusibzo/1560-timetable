from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev68.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.68", "Rev.70")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=68",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=70",{updateViaCache:"none"})',
    1,
)

# Rev70: requested calendar weekend colors.
# Sunday = red, Saturday = blue, including weekday headers and date numbers.
css = r'''
/* Rev70: Sunday red / Saturday blue. */
.calendar-week span:first-child{
  color:#df3a43!important;
}
.calendar-week span:last-child{
  color:#1767c8!important;
}
.calendar-day.sun .solar-no{
  color:#df3a43!important;
}
.calendar-day.sat .solar-no{
  color:#1767c8!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev70-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="70";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
