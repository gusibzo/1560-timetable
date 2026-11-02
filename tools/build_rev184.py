"""Boost alarm volume and expose supported audio output selection with phone help."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev183.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

(root / 'alarm.html').write_text(Path(__file__).with_name('rev184_alarm.html').read_text(encoding='utf-8'), encoding='utf-8')
index = root / 'index.html'
html = index.read_text(encoding='utf-8')
if 'Rev.183' not in html:
    raise RuntimeError('Expected Rev183')
html = html.replace('Rev.183', 'Rev.184').replace('sw.js?v=183', 'sw.js?v=184')
html = re.sub(r'(channel=\d+&amp;v=)183', r'\g<1>184', html)
html = html.replace("url.searchParams.set('v', '183');", "url.searchParams.set('v', '184');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=183', 'sw.js?v=184').replace('Rev.183', 'Rev.184'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev183-v1', '1560-timetable-rev184-v1').replace('REVISION="183"', 'REVISION="184"'), encoding='utf-8')
