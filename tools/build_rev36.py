from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev35.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.35", "Rev.36")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=35",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=36",{updateViaCache:"none"})',
    1,
)

# Open Roadplus in the same Samsung Internet tab. The supplied Roadplus URL does
# not encode a unique CCTV id; using the same tab lets Roadplus reuse the phone's
# saved/last CCTV state, which is currently Yangjae on the user's device.
pattern = re.compile(
    r'<a href="https://www\.roadplus\.co\.kr/main#?"[^>]*>🛣️ 도로교통</a>'
)
replacement = '<a href="https://www.roadplus.co.kr/main#" rel="noreferrer" referrerpolicy="no-referrer" aria-label="로드플러스 양재 CCTV 열기">🛣️ 도로교통</a>'
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise RuntimeError("Roadplus traffic button was not found")

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev36-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="36";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
