from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev143.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old
index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=143",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.143' not in html:
    raise RuntimeError('Expected Rev143 input')

anchor = '          <a class="gyeonggi-badge coworker-badge"'
if html.count(anchor) != 1:
    raise RuntimeError('Expected coworker button')
html = html.replace(anchor, '''          <button id="outdoorTempBtn" type="button" aria-haspopup="dialog" aria-controls="outdoorTempDialog" aria-label="현재 위치 외부 온도 확인"><small>외부 온도</small><strong id="outdoorTempValue">확인 중</strong></button>
''' + anchor, 1)
anchor = '      <a class="traffic-choice seoul-toll"'
if html.count(anchor) != 1:
    raise RuntimeError('Expected Seoul toll CCTV link')
html = html.replace(anchor, '''      <a class="traffic-choice banpo" id="banpoCctvLink" href="https://rtt.map.naver.com/end-traffic/bridges/cctv/web/home?cctvGroupId=17&amp;channel=6043&amp;seq=3" rel="noreferrer" referrerpolicy="no-referrer" aria-label="반포IC CCTV 바로 열기">
        <span class="ico">📹</span><span class="txt"><strong>반포IC CCTV · 바로보기</strong><small>경부고속도로 반포IC · 경찰청 CCTV</small></span>
      </a>
''' + anchor, 1)
html = html.replace('aria-label="양재, 서울톨게이트, 염곡사거리,', 'aria-label="양재, 반포IC, 서울톨게이트, 염곡사거리,', 1)
modal = '''
<dialog id="outdoorTempDialog" aria-labelledby="outdoorTempTitle">
  <div class="outdoor-temp-head"><h2 id="outdoorTempTitle">현재 위치 외부 온도</h2><button id="outdoorTempClose" type="button" aria-label="닫기">×</button></div>
  <p id="outdoorTempMessage">현재 위치를 확인하고 있습니다.</p>
  <p id="outdoorTempUpdate"></p>
  <p class="outdoor-temp-note">현재 위치 주변의 날씨 자료로 계산한 외부 온도입니다. 휴대폰이나 실내 온도를 측정하는 기능은 아닙니다.<br>날씨를 확인할 때 대략적인 위치를 Open-Meteo에 전달합니다.</p>
  <button id="outdoorTempRefresh" type="button">위치·온도 다시 불러오기</button>
  <a class="outdoor-temp-source" href="https://open-meteo.com/" target="_blank" rel="noopener noreferrer">날씨 제공: Open-Meteo</a>
</dialog>
'''
css = Path(__file__).with_name('rev144_outdoor.css').read_text(encoding='utf-8')
js = Path(__file__).with_name('rev144_outdoor.js').read_text(encoding='utf-8')
html = html.replace('</head>', '<style id="rev144-outdoor-style">\n' + css + '\n</style>\n</head>', 1)
html = html.replace('</body>', modal + '\n<script id="rev144-outdoor-script">\n' + js + '\n</script>\n</body>', 1)
html = html.replace('Rev.143', 'Rev.144').replace(registration, registration.replace('v=143', 'v=144'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev143-v1', '1560-timetable-rev144-v1').replace('REVISION="143"', 'REVISION="144"')
sw.write_text(text, encoding='utf-8')
