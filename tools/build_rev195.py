"""Publish the improved arrival detection and timetable colors."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev194.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.194', 'Rev.195').replace('sw.js?v=194', 'sw.js?v=195')
    html = re.sub(r'(channel=\d+&amp;v=)194', r'\g<1>195', html)
    html = html.replace("url.searchParams.set('v', '194');", "url.searchParams.set('v', '195');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev194-v1', '1560-timetable-rev195-v1')
sw.write_text(code.replace('REVISION="194"', 'REVISION="195"'), encoding='utf-8')
