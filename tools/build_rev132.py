from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev131.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.131", "Rev.132")
css = Path(__file__).with_name("rev132_light_dividers.css").read_text(encoding="utf-8")
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", "\n" + css + "\n</style>", 1)

registration = 'navigator.serviceWorker.register("./sw.js?v=131",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev131 service worker registration is missing")
text = text.replace(registration, registration.replace("v=131", "v=132"), 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev132-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="132";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
