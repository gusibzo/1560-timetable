from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev146.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=146",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.146' not in html:
    raise RuntimeError('Expected Rev146 input')

style = '''<style id="rev147-outdoor-text">
#outdoorTempBtn,#outdoorTempBtn small,#outdoorTempValue{color:#ffff00}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.146', 'Rev.147').replace(registration, registration.replace('v=146', 'v=147'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev146-v1', '1560-timetable-rev147-v1').replace('REVISION="146"', 'REVISION="147"')
sw.write_text(text, encoding='utf-8')
