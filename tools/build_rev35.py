from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev34.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.34", "Rev.35")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=34",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=35",{updateViaCache:"none"})',
    1,
)

# Open the authenticated employee-family mobile page in the same Samsung Internet tab.
# Using the canonical www host, the exact intranet path and no-referrer avoids the
# restricted custom-tab page and preserves the browser's existing Buspia login cookie.
old_link = '<a class="gyeonggi-badge coworker-badge" href="https://buspia.co.kr/m/" target="_blank" rel="noopener noreferrer" aria-label="사우가족 열기"><span class="bus">💙</span><span>사우가족</span></a>'
new_link = '<a class="gyeonggi-badge coworker-badge" href="https://www.buspia.co.kr/m/intranet/" rel="noreferrer" referrerpolicy="no-referrer" aria-label="사우가족 열기"><span class="bus">💙</span><span>사우가족</span></a>'
if old_link not in text:
    raise RuntimeError("Rev34 coworker-family link was not found")
text = text.replace(old_link, new_link, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev35-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="35";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
