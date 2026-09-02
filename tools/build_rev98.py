from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev97.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.97", "Rev.98")

old_kcc_block = r'''      <a class="traffic-choice kcc" href="https://map.naver.com/p/search/KCC%20%EB%B3%B8%EC%82%AC%20%EC%84%9C%EC%9A%B8%20%EC%84%9C%EC%B4%88%EA%B5%AC%20%EC%82%AC%ED%8F%89%EB%8C%80%EB%A1%9C%20344" rel="noopener noreferrer" aria-label="네이버지도에서 KCC 본사 앞 주변 CCTV 지도 열기">
        <span class="ico">📹</span><span class="txt"><strong>KCC 본사 앞 주변 CCTV</strong><small>네이버지도에서 사평대로 344를 정확히 열기</small></span>
      </a>
      <div class="traffic-note">KCC 본사 버튼은 서울 서초구 사평대로 344를 네이버지도에서 정확히 엽니다. 지도 오른쪽의 테마·레이어 버튼에서 “CCTV”를 켠 뒤 가까운 카메라 아이콘을 누르세요.</div>'''

new_kcc_block = r'''      <a class="traffic-choice kcc" href="https://map.naver.com/p/search/KCC%20%EB%B3%B8%EC%82%AC%20%EC%84%9C%EC%9A%B8%20%EC%84%9C%EC%B4%88%EA%B5%AC%20%EC%82%AC%ED%8F%89%EB%8C%80%EB%A1%9C%20344" rel="noopener noreferrer" aria-label="네이버지도에서 KCC 본사 앞 주변 CCTV 지도 열기">
        <span class="ico">📹</span><span class="txt"><strong>KCC 본사 앞 주변 CCTV</strong><small>네이버지도에서 사평대로 344를 정확히 열기</small></span>
      </a>
      <a class="traffic-choice gosaek" href="https://map.naver.com/p/search/%ED%95%98%EC%9D%B4%EB%B2%84%EC%8A%A4%20%EC%88%98%EC%9B%90%EA%B3%A0%EC%83%89%20%EC%88%98%EC%86%8C%EC%B6%A9%EC%A0%84%EC%86%8C%20%EA%B2%BD%EA%B8%B0%20%EC%88%98%EC%9B%90%EC%8B%9C%20%EA%B6%8C%EC%84%A0%EA%B5%AC%20%EA%B3%A0%EC%83%89%EB%8F%99%201196" rel="noopener noreferrer" aria-label="네이버지도에서 하이버스 수원고색 수소충전소 열기">
        <span class="ico">⛽</span><span class="txt"><strong>고색동 수소충전소 주변 CCTV</strong><small>하이버스 수원고색 · 권선구 고색동 1196</small></span>
      </a>
      <div class="traffic-note">KCC 본사와 고색동 수소충전소 버튼은 네이버지도를 엽니다. 지도 오른쪽의 테마·레이어 버튼에서 “CCTV”를 켠 뒤 가까운 카메라 아이콘을 누르세요.</div>'''

if old_kcc_block not in text:
    raise RuntimeError("Rev97 KCC traffic shortcut was not found")
text = text.replace(old_kcc_block, new_kcc_block, 1)
text = text.replace(
    'aria-label="양재, 염곡사거리, KCC 본사 도로 CCTV 선택"',
    'aria-label="양재, 염곡사거리, KCC 본사, 고색동 수소충전소 주변 CCTV 선택"',
    1,
)

rev98_css = r'''

/* Rev98: Gosaek-dong hydrogen station shortcut in the road-traffic chooser. */
.traffic-choice.gosaek{
  border-color:#24998f!important;
  background:linear-gradient(135deg,#e8fffb 0%,#f9fffd 100%)!important;
}
.traffic-choice.gosaek strong{color:#08776f!important}
.traffic-choice.gosaek small{color:#356d68!important}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev98_css + "</style>", 1)

text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=97",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=98",{updateViaCache:"none"})',
    1,
)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev98-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="98";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
