from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev154.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=154",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.154' not in html:
    raise RuntimeError('Expected Rev154 input')
if not (root / 'icons/bus-marker-neon.png').is_file():
    raise RuntimeError('Fluorescent-yellow bus marker is missing')

style = '''<style id="rev155-neon-bus-background">
body .grid tbody td.next > .time{
  background-image:url("./icons/bus-marker-neon.png")!important;
  background-color:#eeff00!important;
}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.154', 'Rev.155').replace(registration, registration.replace('v=154', 'v=155'), 1)
index.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev154-v1', '1560-timetable-rev155-v1').replace('REVISION="154"', 'REVISION="155"')
core_asset = '"./icons/icon-192.png"'
if text.count(core_asset) != 1:
    raise RuntimeError('Expected existing core icon cache entry')
text = text.replace(core_asset, core_asset + ',"./icons/bus-marker-neon.png"', 1)
sw.write_text(text, encoding='utf-8')
