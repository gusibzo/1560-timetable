from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev61.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.61", "Rev.62")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=61",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=62",{updateViaCache:"none"})',
    1,
)

# Rev62: simplify today's work briefing to the two items needed while driving:
# current departure and next departure. The remaining-departure count and
# final-departure card are intentionally removed from the visible dashboard.
old_cards = '''      <div class="rev57-briefing-item"><span class="rev57-briefing-k">남은 출발</span><strong id="rev57-remaining" class="rev57-briefing-v">—</strong></div>
      <div class="rev57-briefing-item"><span class="rev57-briefing-k">막차 출발</span><strong id="rev57-last" class="rev57-briefing-v">—</strong></div>
'''
if old_cards not in text:
    raise RuntimeError("Rev57 remaining/last briefing cards not found")
text = text.replace(old_cards, "", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev62-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="62";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
