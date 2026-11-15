"""Publish the updated trip timer and arrival chime."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev196.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.196', 'Rev.197').replace('sw.js?v=196', 'sw.js?v=197')
    html = re.sub(r'(channel=\d+&amp;v=)196', r'\g<1>197', html)
    html = html.replace("url.searchParams.set('v', '196');", "url.searchParams.set('v', '197');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev196-v1', '1560-timetable-rev197-v1')
sw.write_text(code.replace('REVISION="196"', 'REVISION="197"'), encoding='utf-8')
