from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev149.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=149",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.149' not in html:
    raise RuntimeError('Expected Rev149 input')

style = '''<style id="rev150-blue-bus-border">
/* Blue outline for the live bus marker, including narrow phone layouts. */
body .grid tbody td.next > .time{box-shadow:0 0 0 2px #1e63d6!important}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.149', 'Rev.150').replace(registration, registration.replace('v=149', 'v=150'), 1)
index.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev149-v1', '1560-timetable-rev150-v1').replace('REVISION="149"', 'REVISION="150"')
sw.write_text(text, encoding='utf-8')
