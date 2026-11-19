"""Add the Android 1560B route recorder to the 경기버스 menu."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev205.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.205', 'Rev.206').replace('sw.js?v=205', 'sw.js?v=206')
    html = re.sub(r'(channel=\d+&amp;v=)205', r'\g<1>206', html)
    html = html.replace("url.searchParams.set('v', '205');", "url.searchParams.set('v', '206');")
    if name == 'index.html':
        insert_before = '    <a id="rev110-bus-search"'
        if html.count(insert_before) != 1:
            raise RuntimeError('Expected one 경기버스 menu')
        link = ('    <a id="route-video-1560b" href="./route-video.html" data-route-video>'
                '● 1560B 노선 녹화</a>\n')
        html = html.replace(insert_before, link + insert_before, 1)
        style = ('<style id="route-video-style">\n'
                 '#route-video-1560b{display:flex;align-items:center;justify-content:center;min-height:48px;'
                 'margin-top:12px;border-radius:12px;background:#9f282a;color:#fff;'
                 'text-decoration:none;font-weight:850;font-size:16px;touch-action:manipulation}\n'
                 '</style>\n')
        html = html.replace('</head>', style + '</head>', 1)
        script = '<script src="./route-video-link.js?v=206" defer></script>\n'
        html = html.replace('</body>', script + '</body>', 1)
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8')
code = code.replace('1560-timetable-rev205-v1', '1560-timetable-rev206-v1')
code = code.replace('REVISION="205"', 'REVISION="206"')
code = code.replace('["./alarm.html", "./timer-records.html"]',
                    '["./alarm.html", "./timer-records.html", "./route-video.html"]')
sw.write_text(code, encoding='utf-8')
