from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base = Path(__file__).with_name("build_rev142.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old

index = root / "index.html"
html = index.read_text(encoding="utf-8")
registration = 'navigator.serviceWorker.register("./sw.js?v=142",{updateViaCache:"none"})'
if html.count(registration) != 1 or "Rev.142" not in html:
    raise RuntimeError("Expected Rev142 before fixing the bus column rails")

# Remove the old pointer/touch/focus handlers rather than competing with them.
pattern = r'<script>\s*\(\(\) => \{\n  const rows = document.getElementById\("rows"\);\n  if \(!rows\) return;\n  let active = -1;[\s\S]*?\n\}\)\(\);\s*</script>'
html, count = re.subn(pattern, "", html)
if count != 1:
    raise RuntimeError("Expected exactly one pointer-driven column script")

# The same td.next class draws the bus. CSS follows it immediately after each
# clock update or table render, without event listeners or stored selection.
selector = ".grid tbody#rows > tr > td.rev135-cursor-column {"
if html.count(selector) != 1:
    raise RuntimeError("Expected the existing two-sided rail style")
selectors = ",\n".join(
    f".grid:has(td.next:nth-child({column})) > tbody#rows > tr > td:nth-child({column})"
    for column in range(2, 7)
)
html = html.replace(selector, selectors + " {", 1)
html = html.replace(
    "/* The raised vertical edge follows the pointed-to column. */",
    "/* Rev143: both vertical rails stay on the current bus icon's column. */",
    1,
)
if "rev135-cursor-column" in html:
    raise RuntimeError("Old pointer-driven rail code remains")

html = html.replace("Rev.142", "Rev.143")
html = html.replace(registration, registration.replace("v=142", "v=143"), 1)
index.write_text(html, encoding="utf-8")

sw = root / "sw.js"
text = sw.read_text(encoding="utf-8")
text = text.replace("1560-timetable-rev142-v1", "1560-timetable-rev143-v1")
text = text.replace('REVISION="142"', 'REVISION="143"')
sw.write_text(text, encoding="utf-8")
