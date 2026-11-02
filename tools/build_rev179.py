"""Show a compact clock icon above the bus without a visible alarm time."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev178.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
label = '<span class="rev178-alarm-title">⏰ 알람</span>'
if html.count(label) != 1 or 'Rev.178' not in html:
    raise RuntimeError('Expected the Rev178 bus alarm shortcut')
html = html.replace(label, '<span class="rev178-alarm-title" aria-hidden="true">⏰</span>', 1)
style = '''<style id="rev179-compact-alarm-icon">
/* Keep only the clock visible; its accessible name still includes the next alarm. */
#alarmQuick{
  width:32px!important;min-width:32px!important;height:28px!important;min-height:28px!important;
  flex:0 0 32px!important;padding:0!important;gap:0!important;
  border:0!important;border-radius:50%!important;background:transparent!important;
  box-shadow:none!important;font-size:22px!important;line-height:1!important;
}
#alarmQuickTime{display:none!important}
.grid tbody td.rev178-has-alarm > #alarmQuick{margin-bottom:3px!important}
/* The small visible icon keeps a generous invisible touch area. */
#alarmQuick::after{content:"";position:absolute;inset:-8px;display:block;border-radius:50%}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.178', 'Rev.179').replace('sw.js?v=178', 'sw.js?v=179')
html = re.sub(r'(channel=\d+&amp;v=)178', r'\g<1>179', html)
html = html.replace("url.searchParams.set('v', '178');", "url.searchParams.set('v', '179');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=178', 'sw.js?v=179').replace('Rev.178', 'Rev.179'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev178-v1', '1560-timetable-rev179-v1').replace('REVISION="178"', 'REVISION="179"'), encoding='utf-8')
