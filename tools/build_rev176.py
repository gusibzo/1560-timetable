"""Rename the shared board shortcut to the resource room."""
from pathlib import Path
import re
import runpy
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
base=Path(__file__).with_name('build_rev175.py')
old=sys.argv[:]
try:
    sys.argv=[str(base),str(root)]
    runpy.run_path(str(base),run_name='__main__')
finally:
    sys.argv=old
index=root/'index.html'
html=index.read_text(encoding='utf-8')
old_link='<a id="busBoardBtn" href="https://bus1560-board.gusibzo.chatgpt.site/" target="_top" aria-label="버스 게시판 열기">📋 게시판</a>'
if html.count(old_link)!=1:
    raise RuntimeError('Expected the current board shortcut')
html=html.replace(old_link,old_link.replace('게시판','자료실'),1)
html=html.replace('Rev.175','Rev.176').replace('sw.js?v=175','sw.js?v=176')
html=re.sub(r'(channel=\d+&amp;v=)175',r'\g<1>176',html)
html=html.replace("url.searchParams.set('v', '175');","url.searchParams.set('v', '176');")
index.write_text(html,encoding='utf-8')
viewer=root/'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=175','sw.js?v=176').replace('Rev.175','Rev.176'),encoding='utf-8')
sw=root/'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev175-v1','1560-timetable-rev176-v1').replace('REVISION="175"','REVISION="176"'),encoding='utf-8')
