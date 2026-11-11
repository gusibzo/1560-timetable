"""Keep completed trips in the browser and publish their records page."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev190.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = (root / 'index.html').read_text(encoding='utf-8')
core = re.search(r'<script id="trip-records-core">[\s\S]+?</script>', index)
if not core:
    raise RuntimeError('Expected the same trip storage script used on the timetable')
template = Path(__file__).with_name('rev191_timer_records.html').read_text(encoding='utf-8')
placeholder = '<!-- TRIP_RECORDS_CORE -->'
if template.count(placeholder) != 1:
    raise RuntimeError('Expected one trip storage script placeholder')
(root / 'timer-records.html').write_text(template.replace(placeholder, core.group()), encoding='utf-8')

for name in ['index.html', 'cctv.html', 'alarm.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.190', 'Rev.191').replace('sw.js?v=190', 'sw.js?v=191')
    html = re.sub(r'(channel=\d+&amp;v=)190', r'\g<1>191', html)
    html = html.replace("url.searchParams.set('v', '190');", "url.searchParams.set('v', '191');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8')
code = code.replace('1560-timetable-rev190-v1', '1560-timetable-rev191-v1').replace('REVISION="190"', 'REVISION="191"')
code = code.replace('const CORE=[', 'const CORE=["./timer-records.html",', 1)
anchor = 'const navigationKey=new URL(url.pathname===new URL("./alarm.html",self.registration.scope).pathname?"./alarm.html":"./index.html",self.registration.scope);'
if code.count(anchor) != 1:
    raise RuntimeError('Expected the existing navigation cache key')
code = code.replace(anchor, '''const ownPage = ["./alarm.html", "./timer-records.html"].find(page =>
    url.pathname === new URL(page, self.registration.scope).pathname
  );
  const navigationKey = new URL(ownPage || "./index.html", self.registration.scope);''', 1)
sw.write_text(code, encoding='utf-8')
