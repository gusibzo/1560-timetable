from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev163.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=163",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.163' not in html:
    raise RuntimeError('Expected Rev163 input')
js = Path(__file__).with_name('rev164_outdoor.js').read_text(encoding='utf-8')
html, count = re.subn(r'<script id="rev144-outdoor-script">[\s\S]*?</script>', lambda m: '<script id="rev144-outdoor-script">\n' + js + '\n</script>', html)
if count != 1:
    raise RuntimeError('Expected one outdoor controller')
anchor = '<strong id="outdoorTempValue">확인 중</strong></span>'
if html.count(anchor) != 1:
    raise RuntimeError('Expected temperature display')
html = html.replace(anchor, anchor + '<span id="outdoorTempBasis"></span>', 1)
html = html.replace('현재 위치 주변의 날씨 자료로 계산한 외부 온도입니다. 휴대폰이나 실내 온도를 측정하는 기능은 아닙니다.', 'Open-Meteo 날씨 모델의 추정 기온입니다. 버스 온도계나 관측소의 실측 기온과 차이가 날 수 있습니다. 위치 오차가 1km보다 크거나 오래된 위치·날씨 자료는 표시하지 않습니다.', 1)
html = html.replace('</head>', '''<style id="rev164-weather-basis">
#outdoorTempBasis{font-size:8px;font-weight:700;line-height:1.1;color:#183d5d;white-space:nowrap}
#outdoorTempBasis:empty{display:none}
</style>
</head>''', 1)
html = html.replace('Rev.163', 'Rev.164').replace(registration, registration.replace('v=163', 'v=164'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev163-v1', '1560-timetable-rev164-v1').replace('REVISION="163"', 'REVISION="164"')
sw.write_text(text, encoding='utf-8')
