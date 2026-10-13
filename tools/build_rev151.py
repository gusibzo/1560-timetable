from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev150.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=150",{updateViaCache:"none"})'
rails = 'box-shadow:inset 1px 0 0 var(--row-dot),inset -1px 0 0 var(--row-dot)!important;'
if html.count(registration) != 1 or 'Rev.150' not in html or html.count(rails) != 1:
    raise RuntimeError('Expected Rev150 input with two bus-column rails')

# Only the two vertical rails change; horizontal accents retain their colors.
html = html.replace(rails, 'box-shadow:inset 1px 0 0 #1e63d6,inset -1px 0 0 #1e63d6!important;', 1)
html = html.replace('Rev.150', 'Rev.151').replace(registration, registration.replace('v=150', 'v=151'), 1)
index.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev150-v1', '1560-timetable-rev151-v1').replace('REVISION="150"', 'REVISION="151"')
sw.write_text(text, encoding='utf-8')
