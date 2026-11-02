"""Add direct numeric alarm entry and local animal recordings."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev182.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

(root / 'alarm.html').write_text(Path(__file__).with_name('rev183_alarm.html').read_text(encoding='utf-8'), encoding='utf-8')
for name in ['rooster.mp3', 'bird.mp3', 'dog.mp3', 'cat.mp3', 'credits.html']:
    if not (root / 'audio' / 'alarms' / name).is_file():
        raise RuntimeError('Missing animal alarm asset: ' + name)

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
if 'Rev.182' not in html:
    raise RuntimeError('Expected Rev182')
html = html.replace('Rev.182', 'Rev.183').replace('sw.js?v=182', 'sw.js?v=183')
html = re.sub(r'(channel=\d+&amp;v=)182', r'\g<1>183', html)
html = html.replace("url.searchParams.set('v', '182');", "url.searchParams.set('v', '183');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=182', 'sw.js?v=183').replace('Rev.182', 'Rev.183'), encoding='utf-8')
sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev182-v1', '1560-timetable-rev183-v1').replace('REVISION="182"', 'REVISION="183"')
code = code.replace('const CORE=[', 'const CORE=["./alarm.html","./alarm.webmanifest","./audio/alarms/rooster.mp3","./audio/alarms/bird.mp3","./audio/alarms/dog.mp3","./audio/alarms/cat.mp3","./audio/alarms/credits.html",', 1)
# Keep the standalone alarm page separate from the timetable's offline entry.
anchor = '  event.respondWith((async()=>{\n    const cache=await caches.open(CACHE_NAME);'
if code.count(anchor) != 1:
    raise RuntimeError('Expected the generic navigation cache')
code = code.replace(anchor, '  const navigationKey=new URL(url.pathname===new URL("./alarm.html",self.registration.scope).pathname?"./alarm.html":"./index.html",self.registration.scope);\n' + anchor, 1)
code = code.replace('const key=new Request(new URL("./index.html",self.registration.scope));', 'const key=new Request(navigationKey);', 1)
code = code.replace('cache.match(new URL("./index.html",self.registration.scope))', 'cache.match(navigationKey)', 1)
sw.write_text(code, encoding='utf-8')
