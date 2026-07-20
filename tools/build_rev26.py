from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev25.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.25", "Rev.26")

# Use TMAP's official app-launch page for the left button.
# Keep the right button on the separate web route page.
text = text.replace(
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/tmap.jsp?scheme=tmap" rel="noopener noreferrer">🧭 T맵</a>',
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/run.jsp" rel="noopener noreferrer">🧭 T맵 실행</a>',
)
text = text.replace(
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" rel="noopener noreferrer">🚏 T맵 길찾기</a>',
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" rel="noopener noreferrer">🚏 T맵 길찾기</a>',
)

# Guard against older generated markup variants.
text = text.replace(
    'href="https://www.tmap.co.kr/tmap2/mobile/tmap.jsp?scheme=tmap"',
    'href="https://www.tmap.co.kr/tmap2/mobile/run.jsp"',
)
text = text.replace('>🧭 T맵</a>', '>🧭 T맵 실행</a>', 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev26-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
