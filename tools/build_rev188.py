"""Keep alarm checkpoints and missed occurrences across page suspension/reload."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev187.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old
(root / 'alarm.html').write_text(Path(__file__).with_name('rev188_alarm.html').read_text(encoding='utf-8'), encoding='utf-8')
for name in ['index.html', 'cctv.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.187', 'Rev.188').replace('sw.js?v=187', 'sw.js?v=188')
    html = re.sub(r'(channel=\d+&amp;v=)187', r'\g<1>188', html)
    html = html.replace("url.searchParams.set('v', '187');", "url.searchParams.set('v', '188');")
    page.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev187-v1', '1560-timetable-rev188-v1').replace('REVISION="187"', 'REVISION="188"'), encoding='utf-8')
