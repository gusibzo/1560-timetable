from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev47.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.47", "Rev.48")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=47",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=48",{updateViaCache:"none"})',
    1,
)

# Rev48: use the exact TOPIS CCTV page as a simple direct link.
# Remove the Rev47 clipboard interception so the browser follows the link normally.
text = text.replace(
    '<strong>염곡사거리 CCTV</strong><small>검색어 “염곡사거리” 자동복사 · CCTV 전용화면</small>',
    '<strong>염곡사거리 CCTV</strong><small>서울 TOPIS CCTV 전용화면 바로 열기</small>',
    1,
)
text = re.sub(
    r'\s*<div class="yeomgok-copy-tip">.*?</div>',
    '',
    text,
    count=1,
    flags=re.S,
)
text = text.replace(
    '염곡사거리 버튼을 누르면 “염곡사거리”가 자동 복사되고 서울시 TOPIS CCTV 전용화면이 열립니다. CCTV 검색칸을 눌러 붙여넣기 → 검색 → 염곡사거리를 선택하면 구룡사 ↓ · 양재IC ↑ 방향 영상을 볼 수 있습니다.',
    '염곡사거리 버튼은 서울시 TOPIS CCTV 전용화면을 바로 엽니다. 마지막으로 보던 CCTV 상태가 유지되면 염곡사거리 영상이 바로 보일 수 있습니다.',
    1,
)

# Remove only the Rev47 clipboard-copy script.
text, removed = re.subn(
    r'\s*<script>\s*\(function\(\)\{\s*const link=document\.getElementById\("yeomgokCctvLink"\);.*?</script>',
    '',
    text,
    count=1,
    flags=re.S,
)
if removed != 1:
    raise RuntimeError("Rev47 Yeomgok clipboard script was not found")

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev48-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="48";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
