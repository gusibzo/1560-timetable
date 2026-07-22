from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev32.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.32", "Rev.33")

# Ask the browser for the current service-worker file instead of silently
# continuing with the deleted/obsolete worker that kept Rev29 on screen.
old_register = 'navigator.serviceWorker.register("./sw.js")'
new_register = 'navigator.serviceWorker.register("./sw.js?v=33",{updateViaCache:"none"})'
if old_register not in text:
    raise RuntimeError("service-worker registration line was not found")
text = text.replace(old_register, new_register, 1)

# Avoid browser HTTP cache for the main document as an additional safeguard.
cache_meta = '''\n<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">\n<meta http-equiv="Pragma" content="no-cache">\n<meta http-equiv="Expires" content="0">'''
text = text.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">' + cache_meta, 1)

text = text.replace(
    "※ 네이버지도 버튼을 누르는 순간 지도 창이 먼저 닫힙니다. 지도에서 나오면 바로 1560 시간표가 보입니다.",
    "※ 네이버지도 버튼을 누르면 이 창이 먼저 닫힙니다. 지도 앱에서 나오면 열린 시간표가 바로 보입니다.",
    1,
)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js recovery worker is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev33-v2";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="33";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
