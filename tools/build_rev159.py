from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev158.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=158",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.158' not in html:
    raise RuntimeError('Expected Rev158 input')

for class_name, expected in [('official-gap-guide', 3), ('route-gap-guide', 1)]:
    matches = list(re.finditer(r'<section class="' + class_name + r'"[\s\S]*?</section>', html))
    if len(matches) != 1:
        raise RuntimeError('Expected one ' + class_name)
    section = matches[0].group()
    updated, count = re.subn(r'2시간(\s*)35분', r'2시간\g<1>40분', section)
    if count != expected:
        raise RuntimeError('Unexpected duration count in ' + class_name)
    html = html[:matches[0].start()] + updated + html[matches[0].end():]

html = html.replace('Rev.158', 'Rev.159').replace(registration, registration.replace('v=158', 'v=159'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev158-v1', '1560-timetable-rev159-v1').replace('REVISION="158"', 'REVISION="159"')
sw.write_text(text, encoding='utf-8')
