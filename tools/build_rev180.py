"""Make the bus alarm icon wider and shorter."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev179.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
if 'Rev.179' not in html or 'id="rev179-compact-alarm-icon"' not in html:
    raise RuntimeError('Expected the Rev179 compact alarm icon')
style = '''<style id="rev180-wide-short-alarm">
#alarmQuick{
  width:44px!important;min-width:44px!important;flex-basis:44px!important;
  height:22px!important;min-height:22px!important;
}
#alarmQuick > .rev178-alarm-title{
  display:block;transform:scale(1.35,.8);transform-origin:center;
}
/* Preserve a 44px touch area around the flatter visible clock. */
#alarmQuick::after{inset:-11px 0}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.179', 'Rev.180').replace('sw.js?v=179', 'sw.js?v=180')
html = re.sub(r'(channel=\d+&amp;v=)179', r'\g<1>180', html)
html = html.replace("url.searchParams.set('v', '179');", "url.searchParams.set('v', '180');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=179', 'sw.js?v=180').replace('Rev.179', 'Rev.180'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev179-v1', '1560-timetable-rev180-v1').replace('REVISION="179"', 'REVISION="180"'), encoding='utf-8')
