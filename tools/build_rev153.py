from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev152.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=152",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.152' not in html:
    raise RuntimeError('Expected Rev152 input')

style = '''<style id="rev153-large-bus-close">
#rev110-bus-title{padding-inline:44px}
#rev110-bus-close{
  width:48px;height:48px;min-width:48px;min-height:48px;
  display:grid;place-items:center;padding:0;
  font-family:inherit;font-size:38px;font-weight:700;line-height:1;
  border:1px solid #a9c9eb;background:#081e37;color:#fff;
  touch-action:manipulation;
}
#rev110-bus-close:focus-visible{outline:3px solid #ffd85d;outline-offset:2px}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.152', 'Rev.153').replace(registration, registration.replace('v=152', 'v=153'), 1)
index.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev152-v1', '1560-timetable-rev153-v1').replace('REVISION="152"', 'REVISION="153"')
sw.write_text(text, encoding='utf-8')
