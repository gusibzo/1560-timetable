from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev156.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=156",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.156' not in html:
    raise RuntimeError('Expected Rev156 input')
anchor = '<strong id="outdoorTempValue">확인 중</strong>'
if html.count(anchor) != 1:
    raise RuntimeError('Expected outdoor reading')
html = html.replace(anchor, '<span class="outdoor-temp-reading"><span id="outdoorWeatherIcon" aria-hidden="true" hidden></span>' + anchor + '</span>', 1)
js = Path(__file__).with_name('rev157_outdoor.js').read_text(encoding='utf-8')
html, count = re.subn(r'<script id="rev144-outdoor-script">[\s\S]*?</script>', lambda m: '<script id="rev144-outdoor-script">\n' + js + '\n</script>', html)
if count != 1:
    raise RuntimeError('Expected exactly one outdoor weather controller')
css = Path(__file__).with_name('rev157_outdoor.css').read_text(encoding='utf-8')
html = html.replace('</head>', '<style id="rev157-outdoor-weather">\n' + css + '\n</style>\n</head>', 1)
html = html.replace('Rev.156', 'Rev.157').replace(registration, registration.replace('v=156', 'v=157'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev156-v1', '1560-timetable-rev157-v1').replace('REVISION="156"', 'REVISION="157"')
sw.write_text(text, encoding='utf-8')
