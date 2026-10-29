"""Replace the lower weather shortcut with the shared bus board."""
from pathlib import Path
import re
import runpy
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
base=Path(__file__).with_name('build_rev173.py')
old=sys.argv[:]
try:
 sys.argv=[str(base),str(root)]
 runpy.run_path(str(base),run_name='__main__')
finally:sys.argv=old
index=root/'index.html'
html=index.read_text(encoding='utf-8')
old_link='<a href="https://www.weather.go.kr/w/index.do" target="_blank" rel="noopener noreferrer" aria-label="기상청 날씨누리 열기">🌤️ 날씨</a>'
new_link='<a id="busBoardBtn" href="https://bus1560-board.gusibzo.chatgpt.site/" aria-label="버스 게시판 열기">📋 게시판</a>'
if html.count(old_link)!=1:raise RuntimeError('Expected one lower weather shortcut')
html=html.replace(old_link,new_link,1)
# Preserve the exact blue/yellow shortcut styling when the destination changes.
html=html.replace('.info-bar > a[href*="weather.go.kr"]','.info-bar > #busBoardBtn').replace('.info-bar>a[href*="weather.go.kr"]','.info-bar>#busBoardBtn')
html=html.replace('Rev.173','Rev.174').replace('sw.js?v=173','sw.js?v=174')
html=re.sub(r'(channel=\d+&amp;v=)173',r'\g<1>174',html)
html=html.replace("url.searchParams.set('v', '173');","url.searchParams.set('v', '174');")
index.write_text(html,encoding='utf-8')
viewer=root/'cctv.html'
page=viewer.read_text(encoding='utf-8').replace('sw.js?v=173','sw.js?v=174').replace('Rev.173','Rev.174')
viewer.write_text(page,encoding='utf-8')
sw=root/'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev173-v1','1560-timetable-rev174-v1').replace('REVISION="173"','REVISION="174"'),encoding='utf-8')
