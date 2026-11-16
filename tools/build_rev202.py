"""Publish the next departure countdown and bundle trip sounds for offline use."""
from base64 import b64encode
import json
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev201.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.201', 'Rev.202').replace('sw.js?v=201', 'sw.js?v=202')
    html = re.sub(r'(channel=\d+&amp;v=)201', r'\g<1>202', html)
    html = html.replace("url.searchParams.set('v', '201');", "url.searchParams.set('v', '202');")
    if name == 'index.html':
        recordings = {}
        for kind, filename in (('departure', 'departure-ko.mp3'), ('gate', 'kyung-hee-gate-ko.mp3')):
            recordings[kind] = b64encode((root / 'audio' / 'trip' / filename).read_bytes()).decode('ascii')
        anchor = '<script id="rev189-trip-timer">'
        if html.count(anchor) != 1:
            raise RuntimeError('Expected one trip timer controller')
        audio = '<script id="tripVoiceAudio" type="application/json">' + json.dumps(recordings) + '</script>'
        html = html.replace(anchor, audio + '\n' + anchor, 1)
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev201-v1', '1560-timetable-rev202-v1')
sw.write_text(code.replace('REVISION="201"', 'REVISION="202"'), encoding='utf-8')
