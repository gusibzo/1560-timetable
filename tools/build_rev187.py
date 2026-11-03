"""Replace the lion alarm with a short roar using an immutable audio URL."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev186.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'alarm.html', 'cctv.html']:
    path = root / name
    html = path.read_text(encoding='utf-8')
    html = html.replace('Rev.186', 'Rev.187').replace('sw.js?v=186', 'sw.js?v=187')
    html = re.sub(r'(channel=\d+&amp;v=)186', r'\g<1>187', html)
    html = html.replace("url.searchParams.set('v', '186');", "url.searchParams.set('v', '187');")
    if name == 'alarm.html':
        old_url = "lion: './audio/alarms/lion-roar.mp3'"
        if old_url not in html:
            raise RuntimeError('Expected the previous lion recording URL')
        html = html.replace(old_url, "lion: './audio/alarms/lion-roar-v187.mp3'", 1)
    path.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8')
code = code.replace('1560-timetable-rev186-v1', '1560-timetable-rev187-v1')
code = code.replace('REVISION="186"', 'REVISION="187"')
code = code.replace('const CORE=[', 'const CORE=["./audio/alarms/lion-roar-v187.mp3",', 1)
sw.write_text(code, encoding='utf-8')
if not (root / 'audio' / 'alarms' / 'lion-roar-v187.mp3').is_file():
    raise RuntimeError('Missing replacement lion recording')
