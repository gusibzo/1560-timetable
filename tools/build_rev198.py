"""Publish the departure and arrival chime fixes."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev197.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.197', 'Rev.198').replace('sw.js?v=197', 'sw.js?v=198')
    html = re.sub(r'(channel=\d+&amp;v=)197', r'\g<1>198', html)
    html = html.replace("url.searchParams.set('v', '197');", "url.searchParams.set('v', '198');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev197-v1', '1560-timetable-rev198-v1')
sw.write_text(code.replace('REVISION="197"', 'REVISION="198"'), encoding='utf-8')
