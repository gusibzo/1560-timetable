from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev122.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.122", "Rev.123")
anchor = '      <a class="traffic-choice yeomgok"'
# Naver's Gyeongbu road data identifies channel 78 as Seoul tollgate's
# "서울영업소" camera (group 17, order 25).
seoul_link = '''      <a class="traffic-choice seoul-toll" id="seoulTollCctvLink" href="https://rtt.map.naver.com/end-traffic/bridges/cctv/web/home?cctvGroupId=17&amp;channel=78&amp;seq=25" rel="noreferrer" referrerpolicy="no-referrer" aria-label="서울톨게이트 서울영업소 CCTV 바로 열기">
        <span class="ico">📹</span><span class="txt"><strong>서울톨게이트 CCTV</strong><small>경부고속도로 서울영업소 · CCTV 바로보기</small></span>
      </a>
'''
if text.count(anchor) != 1:
    raise RuntimeError("Traffic chooser insertion point is missing or duplicated")
text = text.replace(anchor, seoul_link + anchor, 1)
old_label = 'aria-label="양재, 염곡사거리, KCC 본사, 고색동 수소충전소 주변 CCTV 선택"'
if text.count(old_label) != 1:
    raise RuntimeError("Traffic button accessibility label is missing")
text = text.replace(old_label, 'aria-label="양재, 서울톨게이트, 염곡사거리, KCC 본사, 고색동 수소충전소 주변 CCTV 선택"', 1)
css = """
/* Rev123: Seoul tollgate camera and scrolling for the expanded chooser. */
.traffic-choice.seoul-toll {
  border-color:#8593bd;
  background:linear-gradient(135deg,#edf1ff 0%,#fff 100%);
}
.traffic-choice.seoul-toll strong {color:#334b80}
.traffic-choice.seoul-toll small {color:#53617c}
.traffic-card {
  display:flex;flex-direction:column;
  max-height:calc(100vh - 36px);max-height:calc(100dvh - 36px);
}
.traffic-head {flex-shrink:0}
.traffic-body {
  min-height:0;overflow-y:auto;
  overscroll-behavior:contain;-webkit-overflow-scrolling:touch;
}
"""
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", "\n" + css + "\n</style>", 1)
registration = 'navigator.serviceWorker.register("./sw.js?v=122",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev122 service worker registration is missing")
text = text.replace(registration, registration.replace("v=122", "v=123"), 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev123-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="123";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
