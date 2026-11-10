"""Reduce the trip timer's width and the sticky header's height on phones."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev189.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
css = Path(__file__).with_name('rev190_compact_header.css').read_text(encoding='utf-8')
anchor = '</style>\n<section id="tripTimer"'
if html.count(anchor) != 1:
    raise RuntimeError('Expected the original trip timer style before its panel')
html = html.replace(anchor, '</style>\n<style id="rev190-compact-header">\n' + css + '</style>\n<section id="tripTimer"', 1)
index.write_text(html, encoding='utf-8')

for name in ['index.html', 'cctv.html', 'alarm.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.189', 'Rev.190').replace('sw.js?v=189', 'sw.js?v=190')
    html = re.sub(r'(channel=\d+&amp;v=)189', r'\g<1>190', html)
    html = html.replace("url.searchParams.set('v', '189');", "url.searchParams.set('v', '190');")
    page.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev189-v1', '1560-timetable-rev190-v1').replace('REVISION="189"', 'REVISION="190"'), encoding='utf-8')
