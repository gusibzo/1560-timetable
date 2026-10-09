from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev147.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=147",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.147' not in html:
    raise RuntimeError('Expected Rev147 input')

style = '''<style id="rev148-outdoor-text">
#outdoorTempBtn,#outdoorTempBtn small,#outdoorTempValue{color:#000}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.147', 'Rev.148').replace(registration, registration.replace('v=147', 'v=148'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev147-v1', '1560-timetable-rev148-v1').replace('REVISION="147"', 'REVISION="148"')
sw.write_text(text, encoding='utf-8')
