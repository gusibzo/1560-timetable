from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev155.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=155",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.155' not in html:
    raise RuntimeError('Expected Rev155 input')

js = Path(__file__).with_name('rev156_open_at_bus.js').read_text(encoding='utf-8')
html = html.replace('</body>', '<script id="rev156-open-at-bus">\n' + js + '\n</script>\n</body>', 1)
html = html.replace('Rev.155', 'Rev.156').replace(registration, registration.replace('v=155', 'v=156'), 1)
index.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev155-v1', '1560-timetable-rev156-v1').replace('REVISION="155"', 'REVISION="156"')
sw.write_text(text, encoding='utf-8')
