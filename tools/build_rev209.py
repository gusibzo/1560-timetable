"""Add the browser recorder for routes 1560A and 1560B to the 경기버스 menu."""
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
    html = page.read_text(encoding='utf-8').replace('Rev.205', 'Rev.209').replace('sw.js?v=205', 'sw.js?v=209')
    html = re.sub(r'(channel=\d+&amp;v=)205', r'\g<1>209', html)
    html = html.replace("url.searchParams.set('v', '205');", "url.searchParams.set('v', '209');")
    if name == 'index.html':
        insert_before = '    <a id="rev110-bus-search"'
        if html.count(insert_before) != 1:
            raise RuntimeError('Expected one 경기버스 menu')
        links = ('    <div class="route-video-actions">\n'
                 '      <a href="./route-video.html?start=1#record-A" data-route-video="A">● 1560A 노선 녹화</a>\n'
                 '      <a href="./route-video.html?start=1#record-B" data-route-video="B">● 1560B 노선 녹화</a>\n'
                 '    </div>\n')
        html = html.replace(insert_before, links + insert_before, 1)
        style = ('<style id="route-video-style">\n'
                 '.route-video-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:12px}\n'
                 '.route-video-actions a{display:flex;align-items:center;justify-content:center;min-height:48px;'
                 'padding:8px 4px;border-radius:12px;background:#9f282a;color:#fff;text-align:center;'
                 'text-decoration:none;font-weight:850;font-size:15px;touch-action:manipulation}\n'
                 '</style>\n')
        html = html.replace('</head>', style + '</head>', 1)
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8')
code = code.replace('1560-timetable-rev205-v1', '1560-timetable-rev209-v1')
code = code.replace('REVISION="205"', 'REVISION="209"')
code = code.replace('["./alarm.html", "./timer-records.html"]',
                    '["./alarm.html", "./timer-records.html", "./route-video.html"]')
code = code.replace('const CORE=[', 'const CORE=["./route-video.html","./route-video.js?v=209","./route-video-data/A.json","./route-video-data/B.json",')
sw.write_text(code, encoding='utf-8')
