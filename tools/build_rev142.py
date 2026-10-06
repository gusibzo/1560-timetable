from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base = Path(__file__).with_name("build_rev141.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old

index = root / "index.html"
html = index.read_text(encoding="utf-8")
registration = 'navigator.serviceWorker.register("./sw.js?v=141",{updateViaCache:"none"})'
if html.count(registration) != 1 or "Rev.141" not in html:
    raise RuntimeError("Expected Rev141 before styling the monthly work record")

css = r'''
/* Rev142: black monthly work-record panel with white text. */
#rev58-work-panel {
  background:#000!important;
  border-color:#000!important;
}
#rev58-work-panel,
#rev58-work-panel * {
  color:#fff!important;
}
'''
html = html.replace("</style>", css + "\n</style>", 1)
html = html.replace("Rev.141", "Rev.142")
html = html.replace(registration, registration.replace("v=141", "v=142"), 1)
index.write_text(html, encoding="utf-8")

sw = root / "sw.js"
text = sw.read_text(encoding="utf-8")
text = text.replace("1560-timetable-rev141-v1", "1560-timetable-rev142-v1")
text = text.replace('REVISION="141"', 'REVISION="142"')
sw.write_text(text, encoding="utf-8")
