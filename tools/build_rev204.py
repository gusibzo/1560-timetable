"""Make the reserved departure countdown easier to read on phones."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev203.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.203', 'Rev.204').replace('sw.js?v=203', 'sw.js?v=204')
    html = re.sub(r'(channel=\d+&amp;v=)203', r'\g<1>204', html)
    html = html.replace("url.searchParams.set('v', '203');", "url.searchParams.set('v', '204');")
    if name == 'index.html':
        label = '<span id="tripCountdown" hidden>출발까지 '
        if html.count(label) != 1:
            raise RuntimeError('Expected one reserved departure countdown')
        html = html.replace(label, '<span id="tripCountdown" hidden><span class="trip-countdown-label">출발까지</span> ', 1)
        css = '''<style id="rev204-departure-countdown">
#tripTimer .trip-times{grid-template-columns:minmax(0,1fr) auto;align-items:baseline}
#tripTimer #tripCountdown{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 7px;min-width:0;white-space:normal;font-size:16px;font-weight:800;line-height:1.25}
#tripTimer #tripCountdown[hidden]{display:none}
#tripCountdown .trip-countdown-label{white-space:nowrap}
#tripTimer #tripRemaining{font-size:clamp(24px,6.5vw,28px);font-weight:950;line-height:1.15;white-space:nowrap;font-variant-numeric:tabular-nums;color:#82caff}
</style>
'''
        html = html.replace('</head>', css + '</head>', 1)
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev203-v1', '1560-timetable-rev204-v1')
sw.write_text(code.replace('REVISION="203"', 'REVISION="204"'), encoding='utf-8')
