"""Publish the Korean trip announcements and cache their audio."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev198.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.198', 'Rev.199').replace('sw.js?v=198', 'sw.js?v=199')
    html = re.sub(r'(channel=\d+&amp;v=)198', r'\g<1>199', html)
    html = html.replace("url.searchParams.set('v', '198');", "url.searchParams.set('v', '199');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev198-v1', '1560-timetable-rev199-v1')
code = code.replace('REVISION="198"', 'REVISION="199"')
code = code.replace(
    'const CORE=[',
    'const CORE=["./audio/trip/departure-ko.mp3","./audio/trip/kyung-hee-gate-ko.mp3",',
    1,
)
sw.write_text(code, encoding='utf-8')
