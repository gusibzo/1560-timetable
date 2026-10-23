from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev157.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=157",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.157' not in html:
    raise RuntimeError('Expected Rev157 input')

# Apply the clarified 25 -> 30 minute change to both running-time guides.
# These are duration labels, not departure times in the main timetable.
for class_name, expected in [('official-gap-guide', 2), ('route-gap-guide', 7)]:
    pattern = r'<section class="' + class_name + r'"[\s\S]*?</section>'
    matches = list(re.finditer(pattern, html))
    if len(matches) != 1:
        raise RuntimeError('Expected one ' + class_name)
    section = matches[0].group()
    updated, count = re.subn(r'2시간(\s*)25분', r'2시간\g<1>30분', section)
    if count != expected:
        raise RuntimeError('Unexpected duration count in ' + class_name)
    html = html[:matches[0].start()] + updated + html[matches[0].end():]

html = html.replace('Rev.157', 'Rev.158').replace(registration, registration.replace('v=157', 'v=158'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev157-v1', '1560-timetable-rev158-v1').replace('REVISION="157"', 'REVISION="158"')
sw.write_text(text, encoding='utf-8')
