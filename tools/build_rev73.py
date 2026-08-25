from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev72.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.72", "Rev.73")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=72",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=73",{updateViaCache:"none"})',
    1,
)

# Rev73: center only the large elapsed counter inside the left briefing card.
# Keep the trip label aligned normally so the counter itself gets the emphasis.
css = r'''
/* Rev73: center the live departure counter in its card. */
.rev72-counter{
  width:100%!important;
  align-self:center!important;
  text-align:center!important;
  margin-left:auto!important;
  margin-right:auto!important;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev73-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="73";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
