from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev33.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.33", "Rev.34")
text = text.replace('navigator.serviceWorker.register("./sw.js?v=33",{updateViaCache:"none"})', 'navigator.serviceWorker.register("./sw.js?v=34",{updateViaCache:"none"})', 1)

old_top = '<a class="gyeonggi-badge" href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" aria-label="경기버스정보 열기"><span class="bus">🚌</span><span>경기버스</span></a>'
new_top = '''<div class="top-quick-links">
          <button class="gyeonggi-badge" type="button" id="financeBtn" aria-haspopup="dialog" aria-controls="financeModal" aria-label="환율·주식 정보 열기"><span class="bus">💱</span><span>환율·주식</span></button>
          <a class="gyeonggi-badge coworker-badge" href="https://buspia.co.kr/m/" target="_blank" rel="noopener noreferrer" aria-label="사우가족 열기"><span class="bus">💙</span><span>사우가족</span></a>
        </div>'''
if old_top not in text:
    raise RuntimeError("top Gyeonggi Bus badge was not found")
text = text.replace(old_top, new_top, 1)

old_middle = '<button type="button" id="financeBtn" aria-haspopup="dialog" aria-controls="financeModal">💱 환율·주식</button>'
new_middle = '<a href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" aria-label="경기버스정보 열기">🚌 경기버스</a>'
if old_middle not in text:
    raise RuntimeError("middle finance button was not found")
text = text.replace(old_middle, new_middle, 1)

css = r'''
/* Rev34: place the coworker-family shortcut beside finance/stocks. */
.top-quick-links{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.top-quick-links .gyeonggi-badge{font-family:inherit;cursor:pointer;white-space:nowrap}
.top-quick-links .coworker-badge{background:#2b66b1}
@media(max-width:360px){
  .top-quick-links{gap:6px}
  .top-quick-links .gyeonggi-badge{padding:5px 8px;font-size:11px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev34-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="34";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
