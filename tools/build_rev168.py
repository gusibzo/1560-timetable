"""Open the verified Gangnam-daero Kyobo Tower camera directly."""
from pathlib import Path
import json
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev167.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=167",{updateViaCache:"none"})'
if html.count(registration) != 1:
    raise RuntimeError('Expected Rev167 input')
choice = '''<a class="traffic-choice kcc" id="kyoboCctvLink" href="./cctv.html?channel=6929&amp;v=168" aria-label="교보문고 사거리 강남대로 CCTV 바로 열기">
        <span class="ico">📹</span><span class="txt"><strong>교보문고 사거리 CCTV</strong><small>강남대로 · 교보타워R · 논현역 ↔ 강남역</small></span>
      </a>'''
html, count = re.subn(r'<a class="traffic-choice kcc"[\s\S]*?</a>', lambda _: choice, html)
if count != 1:
    raise RuntimeError('Expected one KCC map shortcut')
html = html.replace('KCC 본사와 고색동 수소충전소 버튼은 네이버지도를 엽니다.', '교보문고 사거리 버튼은 CCTV 영상을 바로 엽니다. 고색동 수소충전소 버튼은 네이버지도를 엽니다.', 1)
html = html.replace('KCC 본사, 고색동 수소충전소 주변 CCTV 선택', '교보문고 사거리, 고색동 수소충전소 주변 CCTV 선택', 1)
html = html.replace('Rev.167', 'Rev.168').replace(registration, registration.replace('v=167', 'v=168'), 1)
index.write_text(html, encoding='utf-8')

viewer = root / 'cctv.html'
page = viewer.read_text(encoding='utf-8')
data_pattern = r'(<script id="cctvCameraData" type="application/json">)([\s\S]*?)(</script>)'
match = re.search(data_pattern, page)
if not match:
    raise RuntimeError('Missing CCTV camera catalog')
gangnam = json.loads(Path(__file__).with_name('rev168_gangnam_cameras.json').read_text(encoding='utf-8'))
if next(c for c in gangnam if c['channel'] == 6929) != {'channel': 6929, 'name': '교보타워R', 'road': '강남대로', 'group': 94, 'seq': 4}:
    raise RuntimeError('Unexpected Kyobo camera')
cameras = json.loads(match[2]) + gangnam
if len({c['channel'] for c in cameras}) != len(cameras):
    raise RuntimeError('Duplicate CCTV channels')
data = json.dumps(cameras, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
page = page[:match.start(2)] + data + page[match.end(2):]

def replace_once(before, after):
    global page
    if page.count(before) != 1:
        raise RuntimeError('Expected one occurrence: ' + before)
    page = page.replace(before, after, 1)

replace_once("const cameras = JSON.parse(document.getElementById('cctvCameraData').textContent);", "const catalog = JSON.parse(document.getElementById('cctvCameraData').textContent);")
anchor = "  const requested = Number(new URLSearchParams(location.search).get('channel'));"
replace_once(anchor, anchor + "\n  const group = catalog.find(camera => camera.channel === requested)?.group || 17;\n  const cameras = catalog.filter(camera => (camera.group || 17) === group);")
replace_once("cctvGroupId:'17',channel:String(camera.channel),seq:String(index + 1)", "cctvGroupId:String(camera.group || 17),channel:String(camera.channel),seq:String(camera.seq || index + 1)")
# Each group keeps its own previous/next order; the direct close link is retained.
page = page.replace('실시간 교통 영상 · Rev.162', '실시간 교통 영상 · Rev.168')
viewer.write_text(page, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev167-v1', '1560-timetable-rev168-v1').replace('REVISION="167"', 'REVISION="168"')
sw.write_text(text, encoding='utf-8')
