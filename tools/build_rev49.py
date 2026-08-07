from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev48.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.48", "Rev.49")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=48",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=49",{updateViaCache:"none"})',
    1,
)

# Rev49: make the two CCTV choices easier to understand at a glance.
text = text.replace(
    '<strong>양재 CCTV</strong><small>경부고속도로 양재 화면 바로 열기</small>',
    '<strong>양재 CCTV · 바로보기</strong><small>경부고속도로 양재 CCTV 화면을 바로 엽니다</small>',
    1,
)
text = text.replace(
    '<strong>염곡사거리 CCTV</strong><small>서울 TOPIS CCTV 전용화면 바로 열기</small>',
    '<strong>염곡사거리 CCTV · TOPIS</strong><small>구룡사 ↓ · 양재IC ↑ 방향 · CCTV 전용화면</small>',
    1,
)
text = text.replace(
    '염곡사거리 버튼은 서울시 TOPIS CCTV 전용화면을 바로 엽니다. 마지막으로 보던 CCTV 상태가 유지되면 염곡사거리 영상이 바로 보일 수 있습니다.',
    '양재는 “바로보기”, 염곡사거리는 “TOPIS”로 구분했습니다. 염곡사거리는 구룡사 ↓ · 양재IC ↑ 방향 CCTV이며, TOPIS가 마지막으로 보던 CCTV 상태를 유지하면 영상이 바로 보일 수 있습니다.',
    1,
)

css = r'''
/* Rev49: clearer, larger CCTV choice labels. */
.traffic-choice strong{
  font-size:19px!important;
  letter-spacing:-.45px!important;
}
.traffic-choice small{
  font-size:12.5px!important;
  line-height:1.35!important;
}
.traffic-choice.yangjae strong{color:#195f9c!important}
.traffic-choice.yeomgok strong{color:#176b43!important}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev49-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="49";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
