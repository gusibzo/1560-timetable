"""Show a live countdown for each alarm without replacing its controls."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev184.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

(root / 'alarm.html').write_text(Path(__file__).with_name('rev185_alarm.html').read_text(encoding='utf-8'), encoding='utf-8')
index = root / 'index.html'
html = index.read_text(encoding='utf-8')
if 'Rev.184' not in html:
    raise RuntimeError('Expected Rev184')
html = html.replace('Rev.184', 'Rev.185').replace('sw.js?v=184', 'sw.js?v=185')
html = re.sub(r'(channel=\d+&amp;v=)184', r'\g<1>185', html)
html = html.replace("url.searchParams.set('v', '184');", "url.searchParams.set('v', '185');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=184', 'sw.js?v=185').replace('Rev.184', 'Rev.185'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev184-v1', '1560-timetable-rev185-v1').replace('REVISION="184"', 'REVISION="185"'), encoding='utf-8')
