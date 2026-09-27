from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev133.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.133", "Rev.134")
fixed_selector = ".grid tbody#rows > tr:nth-child(6) > td {"
if text.count(fixed_selector) != 1:
    raise RuntimeError("Rev133 fixed row selector is missing")
text = text.replace(fixed_selector, ".grid tbody#rows > tr.rev134-cursor-row > td {", 1)
text = text.replace(
    "/* Raise only the divider between timetable rows 6 and 7. */",
    "/* Raise the divider under the row at the cursor or touch point. */",
    1,
)
if text.count("</body>") != 1:
    raise RuntimeError("Closing body is missing")
js = Path(__file__).with_name("rev134_cursor_rail.js").read_text(encoding="utf-8")
text = text.replace("</body>", "<script>\n" + js + "\n</script>\n</body>", 1)

registration = 'navigator.serviceWorker.register("./sw.js?v=133",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev133 service worker registration is missing")
text = text.replace(registration, registration.replace("v=133", "v=134"), 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev134-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="134";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
