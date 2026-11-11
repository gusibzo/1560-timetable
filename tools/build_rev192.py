"""Build the timetable with editable monthly attendance totals."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev191.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
editor = Path(__file__).with_name('rev192_attendance.html').read_text(encoding='utf-8')
pattern = r'function rev68RenderFullAttendance\(\)\{[\s\S]+?(?=const rev68BaseDrawCalendar=drawCalendar;)'
css, script = editor.split('<script>\n', 1)
html, count = re.subn(pattern, lambda _: script.removesuffix('</script>\n') + '\n', html)
if count != 1:
    raise RuntimeError('Expected one monthly attendance renderer')
html = html.replace('</head>', css + '\n</head>', 1)
index.write_text(html, encoding='utf-8')

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.191', 'Rev.192').replace('sw.js?v=191', 'sw.js?v=192')
    html = re.sub(r'(channel=\d+&amp;v=)191', r'\g<1>192', html)
    html = html.replace("url.searchParams.set('v', '191');", "url.searchParams.set('v', '192');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev191-v1', '1560-timetable-rev192-v1')
sw.write_text(code.replace('REVISION="191"', 'REVISION="192"'), encoding='utf-8')
