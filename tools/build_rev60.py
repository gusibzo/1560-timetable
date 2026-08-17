from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev59.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.59", "Rev.60")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=59",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=60",{updateViaCache:"none"})',
    1,
)

# Rev60: make the work-day count self-explanatory by showing when tracking
# started. Rev58 work tracking was introduced on 2026-08-17, so keep that
# inception date visible both in the briefing button and monthly calendar.
css = r'''
/* Rev60: visible work-record tracking start date. */
.rev60-work-start{
  display:block;
  margin-top:3px;
  color:#67746d;
  font-size:9px;
  font-weight:850;
  line-height:1.2;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

old_panel = 'panel.innerHTML=`<div class="rev58-work-summary">월간 근무기록<strong id="rev58-work-count">이번 달 0일</strong></div><button type="button" id="rev58-work-toggle" class="rev58-work-toggle">선택 날짜 근무</button>`;'
new_panel = 'panel.innerHTML=`<div class="rev58-work-summary">월간 근무기록<strong id="rev58-work-count">이번 달 0일</strong><span id="rev60-work-start" class="rev60-work-start">기록 시작 · 2026.8.17</span></div><button type="button" id="rev58-work-toggle" class="rev58-work-toggle">선택 날짜 근무</button>`;'
if old_panel not in text:
    raise RuntimeError("Rev58 calendar work panel markup not found")
text = text.replace(old_panel, new_panel, 1)

old_button = 'btn.textContent=worked?`✅ 오늘 근무 체크됨 · 이번 달 ${count}일`:`🚌 오늘 근무 체크 · 이번 달 ${count}일`;'
new_button = 'btn.textContent=worked?`✅ 오늘 근무 체크됨 · 8/17부터 · 이번 달 ${count}일`:`🚌 오늘 근무 체크 · 8/17부터 · 이번 달 ${count}일`;'
if old_button not in text:
    raise RuntimeError("Rev58 today work button text not found")
text = text.replace(old_button, new_button, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev60-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="60";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
