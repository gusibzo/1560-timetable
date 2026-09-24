from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev130.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.130", "Rev.131")
css = Path(__file__).with_name("rev131_dotted_rows.css").read_text(encoding="utf-8")
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", "\n" + css + "\n</style>", 1)

registration = 'navigator.serviceWorker.register("./sw.js?v=130",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev130 service worker registration is missing")
text = text.replace(registration, registration.replace("v=130", "v=131"), 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev131-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="131";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
