from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev85.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.85", "Rev.86")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=85",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=86",{updateViaCache:"none"})',
    1,
)

# Rev86: remove the glance heading and all three time cards while retaining
# the work-calendar button that Rev58 appends to the same section.
old_briefing = '''  box.setAttribute("aria-label","오늘 근무 브리핑");
  box.innerHTML=`
    <div class="rev57-briefing-head">
      <span class="rev57-briefing-title">🚌 오늘 운행 한눈보기</span>
      <span id="rev57-day" class="rev57-briefing-badge">오늘 시간표</span>
    </div>
    <div class="rev57-briefing-grid">
      <div class="rev57-briefing-item rev74-current-card"><span class="rev57-briefing-k">현재 출발</span><strong id="rev57-current" class="rev57-briefing-v">—</strong></div>
      <div class="rev57-briefing-item rev74-counter-card"><span class="rev57-briefing-k">카운터</span><strong id="rev74-counter" class="rev74-counter">00:00:00</strong></div>
      <div class="rev57-briefing-item rev74-next-card"><span class="rev57-briefing-k">다음 출발</span><strong id="rev57-next" class="rev57-briefing-v">—</strong></div>
    </div>`;'''
new_briefing = '''  box.setAttribute("aria-label","근무일 달력");
  box.innerHTML="";'''
if text.count(old_briefing) != 1:
    raise RuntimeError("Rev85 briefing markup was not found exactly once")
text = text.replace(old_briefing, new_briefing, 1)

rev86_css = '''

/* Rev86: keep only the work-calendar button from the former briefing card. */
.rev57-briefing{
  padding:0!important;
  background:transparent!important;
  border:0!important;
  box-shadow:none!important;
  overflow:visible!important;
}
.rev58-today-work,
.rev58-today-work.checked{margin-top:0!important}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev86_css + "</style>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev86-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="86";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
