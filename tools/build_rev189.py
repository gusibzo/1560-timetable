"""Add a persistent departure/arrival trip timer below the main shortcut row."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev188.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
anchor = '  </div>\n  </div>\n\n  <nav class="switch"'
if html.count(anchor) != 1:
    raise RuntimeError('Expected one end of the shortcut bar and sticky header')
timer = Path(__file__).with_name('rev189_trip_timer.html').read_text(encoding='utf-8')
html = html.replace(anchor, '  </div>\n' + timer + '\n  </div>\n\n  <nav class="switch"', 1)
index.write_text(html, encoding='utf-8')

for name in ['index.html', 'cctv.html', 'alarm.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.188', 'Rev.189').replace('sw.js?v=188', 'sw.js?v=189')
    html = re.sub(r'(channel=\d+&amp;v=)188', r'\g<1>189', html)
    html = html.replace("url.searchParams.set('v', '188');", "url.searchParams.set('v', '189');")
    page.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev188-v1', '1560-timetable-rev189-v1').replace('REVISION="188"', 'REVISION="189"'), encoding='utf-8')
