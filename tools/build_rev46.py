from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev45.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.45", "Rev.46")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=45",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=46",{updateViaCache:"none"})',
    1,
)

# Open TOPIS with Yeomgok Intersection already entered in the search query,
# and make the direction shown in the confirmed CCTV view clear to the user.
old_url = "https://topis.seoul.go.kr/map/openCctvMap.do"
new_url = "https://topis.seoul.go.kr/map/openTotalMap.do?searchTxt=%EC%97%BC%EA%B3%A1%EC%82%AC%EA%B1%B0%EB%A6%AC"
text = text.replace(f'href="{old_url}"', f'href="{new_url}"', 1)
text = text.replace(
    '<strong>염곡사거리 CCTV</strong><small>서울 TOPIS CCTV 지도에서 염곡사거리 카메라 확인</small>',
    '<strong>염곡사거리 CCTV</strong><small>구룡사 ↓ · 양재IC ↑ 방향 · 염곡사거리 검색</small>',
    1,
)
text = text.replace(
    '염곡사거리 버튼은 서울시 TOPIS의 공식 CCTV 지도 화면을 엽니다. 지도에서 염곡사거리의 파란 CCTV 아이콘을 누르면 영상을 볼 수 있습니다.',
    '염곡사거리 버튼은 서울시 TOPIS에서 “염곡사거리” 검색 화면을 바로 엽니다. 검색 결과에서 염곡사거리를 선택한 뒤 파란 CCTV 아이콘을 누르면 구룡사 ↓ · 양재IC ↑ 방향 영상을 볼 수 있습니다.',
    1,
)

# Slightly emphasize the Yeomgok choice so it is easier to spot while stopped.
css = r'''
/* Rev46: clearer Yeomgok CCTV choice and direction cue. */
.traffic-choice.yeomgok{
  background:linear-gradient(180deg,#f7fff9,#e9f7ee)!important;
  border-color:#58a57d!important;
}
.traffic-choice.yeomgok strong{color:#176b43!important}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev46-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="46";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
