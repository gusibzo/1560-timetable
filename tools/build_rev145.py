from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev144.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=144",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.144' not in html:
    raise RuntimeError('Expected Rev144 input')

# Move complete links so labels, styles and camera destinations stay together.
pattern = r'(      <a class="traffic-choice yangjae"[^>]*>.*?</a>\n)(      <a class="traffic-choice banpo"[^>]*>.*?</a>\n)'
html, count = re.subn(pattern, r'\2\1', html, flags=re.S)
if count != 1:
    raise RuntimeError('Expected adjacent Yangjae and Banpo CCTV links')
html = html.replace('aria-label="양재, 반포IC, 서울톨게이트,', 'aria-label="반포IC, 양재, 서울톨게이트,', 1)
html = html.replace('Rev.144', 'Rev.145').replace(registration, registration.replace('v=144', 'v=145'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev144-v1', '1560-timetable-rev145-v1').replace('REVISION="144"', 'REVISION="145"')
sw.write_text(text, encoding='utf-8')
