"""Publish the corrected trip timer colors."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev195.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.195', 'Rev.196').replace('sw.js?v=195', 'sw.js?v=196')
    html = re.sub(r'(channel=\d+&amp;v=)195', r'\g<1>196', html)
    html = html.replace("url.searchParams.set('v', '195');", "url.searchParams.set('v', '196');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev195-v1', '1560-timetable-rev196-v1')
sw.write_text(code.replace('REVISION="195"', 'REVISION="196"'), encoding='utf-8')
