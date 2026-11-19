"""Keep the reserved departure label and countdown on one line."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev204.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

countdown_css = '''<style id="rev205-departure-countdown">
#tripTimer[data-state="scheduled"] .trip-times{
  grid-template-columns:minmax(max-content,1fr) auto;
  align-items:baseline;
}
#tripTimer #tripCountdown{
  white-space:nowrap;
  font-size:16px;
  font-weight:800;
  line-height:1.25;
}
#tripTimer #tripRemaining{
  font:inherit;
  font-variant-numeric:tabular-nums;
  color:#82caff;
}
</style>'''

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.204', 'Rev.205').replace('sw.js?v=204', 'sw.js?v=205')
    html = re.sub(r'(channel=\d+&amp;v=)204', r'\g<1>205', html)
    html = html.replace("url.searchParams.set('v', '204');", "url.searchParams.set('v', '205');")
    if name == 'index.html':
        html, replacements = re.subn(r'<style id="rev204-departure-countdown">[\s\S]*?</style>', countdown_css, html)
        if replacements != 1:
            raise RuntimeError('Expected one reserved departure countdown stylesheet')
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev204-v1', '1560-timetable-rev205-v1')
sw.write_text(code.replace('REVISION="204"', 'REVISION="205"'), encoding='utf-8')
