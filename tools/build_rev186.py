"""Show a licensed lion/tiger recordings and replace the rooster recording."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev185.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

(root / 'alarm.html').write_text(Path(__file__).with_name('rev186_alarm.html').read_text(encoding='utf-8'), encoding='utf-8')
index = root / 'index.html'
html = index.read_text(encoding='utf-8')
if 'Rev.185' not in html:
    raise RuntimeError('Expected Rev185')
html = html.replace('Rev.185', 'Rev.186').replace('sw.js?v=185', 'sw.js?v=186')
html = re.sub(r'(channel=\d+&amp;v=)185', r'\g<1>186', html)
html = html.replace("url.searchParams.set('v', '185');", "url.searchParams.set('v', '186');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=185', 'sw.js?v=186').replace('Rev.185', 'Rev.186'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev185-v1', '1560-timetable-rev186-v1').replace('REVISION="185"', 'REVISION="186"'), encoding='utf-8')

code = sw.read_text(encoding='utf-8')
code = code.replace('const CORE=[', 'const CORE=["./audio/alarms/lion-roar.mp3","./audio/alarms/tiger-roar.mp3","./audio/alarms/tiger-growl.mp3","./audio/alarms/rooster-farm.mp3","./audio/alarms/rooster.mp3?v=186",', 1)
sw.write_text(code, encoding='utf-8')
for name in ['lion-roar.mp3', 'tiger-roar.mp3', 'tiger-growl.mp3', 'rooster-farm.mp3']:
    if not (root / 'audio' / 'alarms' / name).is_file():
        raise RuntimeError('Missing new animal recording: ' + name)
