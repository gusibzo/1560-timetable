"""Publish the recorder with on-demand vehicle and seat data."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev209.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.209', 'Rev.211').replace('sw.js?v=209', 'sw.js?v=211')
    html = re.sub(r'(channel=\d+&amp;v=)209', r'\g<1>211', html)
    html = html.replace("url.searchParams.set('v', '209');", "url.searchParams.set('v', '211');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev209-v1', '1560-timetable-rev211-v1')
code = code.replace('route-video.js?v=209', 'route-video.js?v=211')
sw.write_text(code.replace('REVISION="209"', 'REVISION="211"'), encoding='utf-8')
