"""Publish editable departures in the timetable trip timer."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev199.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.199', 'Rev.200').replace('sw.js?v=199', 'sw.js?v=200')
    html = re.sub(r'(channel=\d+&amp;v=)199', r'\g<1>200', html)
    html = html.replace("url.searchParams.set('v', '199');", "url.searchParams.set('v', '200');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev199-v1', '1560-timetable-rev200-v1')
sw.write_text(code.replace('REVISION="199"', 'REVISION="200"'), encoding='utf-8')
