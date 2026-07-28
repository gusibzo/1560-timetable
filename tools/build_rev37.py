from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev36.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.36", "Rev.37")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=36",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=37",{updateViaCache:"none"})',
    1,
)

# The Roadplus main URL only opens its map because it does not contain the selected
# CCTV state. Use NAVER's dedicated Yangjae highway CCTV viewer URL instead.
old_link = '<a href="https://www.roadplus.co.kr/main#" rel="noreferrer" referrerpolicy="no-referrer" aria-label="로드플러스 양재 CCTV 열기">🛣️ 도로교통</a>'
new_link = '<a href="https://rtt.map.naver.com/end-traffic/bridges/cctv/web/home?cctvGroupId=17&channel=100&seq=10" rel="noreferrer" referrerpolicy="no-referrer" aria-label="경부고속도로 양재 CCTV 바로 열기">🛣️ 도로교통</a>'
if old_link not in text:
    raise RuntimeError("Rev36 Roadplus link was not found")
text = text.replace(old_link, new_link, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev37-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="37";', sw_text)
sw.write_text(sw_text, encoding="utf-8")