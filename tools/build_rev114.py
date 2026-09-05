from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev113.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.113", "Rev.114")

old_blanks = '''    <div class="black">6:20 AM'</div>
    <div class="black"></div>
    <div class="black"></div>'''
new_blanks = '''    <div class="black">6:20 AM'</div>
    <div class="black rev114-empty" aria-hidden="true"></div>
    <div class="black rev114-empty" aria-hidden="true"></div>'''
if old_blanks not in text:
    raise RuntimeError("The two bottom empty cells were not found")
text = text.replace(old_blanks, new_blanks, 1)

rev114_css = r'''

/* Rev114: remove the two unused cells beside the morning departure times. */
.route-gap-guide,
.rev24-gap-grid{background:transparent!important}
.rev24-gap-grid>.rev114-empty{
  visibility:hidden!important;
  border:0!important;
  background:transparent!important;
  box-shadow:none!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev114_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=113",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=114",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev113 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev114-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="114";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
