"""Use an embedded fresh snapshot and request position/data concurrently."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv)>1 else '_site')
base = Path(__file__).with_name('build_rev170.py')
old = sys.argv[:]
try:
    sys.argv = [str(base),str(root)]
    runpy.run_path(str(base),run_name='__main__')
finally:
    sys.argv = old
index = root/'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=170",{updateViaCache:"none"})'
if html.count(registration)!=1:
    raise RuntimeError('Expected Rev170 input')
js = Path(__file__).with_name('rev171_outdoor.js').read_text(encoding='utf-8')
html,count = re.subn(r'<script id="rev170-outdoor-script">[\s\S]*?</script>',lambda _: '<script id="rev171-outdoor-script">\n'+js+'\n</script>',html)
if count!=1:
    raise RuntimeError('Expected weather controller')
html=html.replace('Rev.170','Rev.171').replace(registration,registration.replace('v=170','v=171'),1)
index.write_text(html,encoding='utf-8')
sw=root/'sw.js'
text=sw.read_text(encoding='utf-8').replace('1560-timetable-rev170-v1','1560-timetable-rev171-v1').replace('REVISION="170"','REVISION="171"')
sw.write_text(text,encoding='utf-8')
