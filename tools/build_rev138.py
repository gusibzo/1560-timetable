from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base = Path(__file__).with_name("build_rev137.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old

index = root / "index.html"
html = index.read_text(encoding="utf-8")
registration = 'navigator.serviceWorker.register("./sw.js?v=137",{updateViaCache:"none"})'
if html.count(registration) != 1:
    raise RuntimeError("Rev137 service-worker registration is missing")
html = html.replace(registration, registration.replace("v=137", "v=138"), 1)
index.write_text(html, encoding="utf-8")

sw = root / "sw.js"
text = sw.read_text(encoding="utf-8")
text = text.replace('const CACHE_NAME="1560-timetable-rev137-v1";', 'const CACHE_NAME="1560-timetable-rev138-v1";')
text = text.replace('const REVISION="137";', 'const REVISION="138";')
core = 'const CORE=["./","./index.html","./manifest.webmanifest"];'
if core not in text:
    raise RuntimeError("Core asset list is different from expected Rev137")
text = text.replace(core, 'const CORE=["./","./index.html","./manifest.webmanifest","./icons/icon-192.png","./icons/icon-512.png","./icons/apple-touch-icon.png"];', 1)
sw.write_text(text, encoding="utf-8")
