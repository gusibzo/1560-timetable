from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev27.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.27", "Rev.28")

# Group the route card and the weather/finance/traffic row into one sticky header.
text, opened = re.subn(
    r'(<main class="wrap">\s*)(<section class="plate">)',
    r'\1<div class="sticky-head">\n  \2',
    text,
    count=1,
)
text, closed = re.subn(
    r'(<div class="info-bar">.*?</div>)\s*(<nav class="switch")',
    r'\1\n  </div>\n\n  \2',
    text,
    count=1,
    flags=re.S,
)
if opened != 1 or closed != 1:
    raise RuntimeError("sticky header insertion point was not found")

css = r'''
/* Rev28: keep the top card and utility buttons fixed; scroll the timetable below. */
.sticky-head{
  position:sticky;
  top:0;
  z-index:8800;
  background:var(--bg);
  padding:2px 0 10px;
  margin:-2px 0 10px;
  border-bottom:4px solid #858c95;
  box-shadow:0 10px 18px -16px rgba(0,0,0,.72);
}
.sticky-head .info-bar{margin-bottom:0}
@supports(padding:max(0px)){
  .sticky-head{top:env(safe-area-inset-top,0px)}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev28-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
