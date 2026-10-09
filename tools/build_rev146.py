from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev145.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=145",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.145' not in html:
    raise RuntimeError('Expected Rev145 input')

# Blue bright enough to keep the requested black label and temperature legible.
style = '''<style id="rev146-outdoor-colors">
#outdoorTempBtn{background:#4da6ff;border-color:#2980d3;color:#000}
#outdoorTempBtn small,#outdoorTempValue{color:#000}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.145', 'Rev.146').replace(registration, registration.replace('v=145', 'v=146'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev145-v1', '1560-timetable-rev146-v1').replace('REVISION="145"', 'REVISION="146"')
sw.write_text(text, encoding='utf-8')
