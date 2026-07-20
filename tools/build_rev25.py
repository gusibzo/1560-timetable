from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev24.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.24", "Rev.25")
text = text.replace('aria-label="신논현역 평일 주말 공휴일 운행 간격 안내"', 'aria-label="신논역 13대 평일 주말 공휴일 운행 간격 안내"')
text = text.replace('<div class="gap-station">신논현역</div>', '<div class="gap-station">신논역(13대)</div>')
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev25-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
