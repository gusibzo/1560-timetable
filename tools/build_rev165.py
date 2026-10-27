from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev164.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=164",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.164' not in html:
    raise RuntimeError('Expected Rev164 input')
link = '''<a id="outdoorTempBtn" href="https://weather.naver.com/" target="_blank" rel="noopener noreferrer" aria-label="네이버 날씨에서 외부 온도 확인, 새 창">
            <small>외부 온도</small><strong class="naver-weather-label">네이버 날씨</strong><span class="naver-weather-open">바로 보기 ↗</span>
          </a>'''
html, count = re.subn(r'<button id="outdoorTempBtn"[\s\S]*?</button>', lambda m: link, html)
if count != 1:
    raise RuntimeError('Expected one outdoor temperature tile')
# Retire the estimate fetcher and its modal when switching to a direct weather link.
for pattern in (r'<script id="rev144-outdoor-script">[\s\S]*?</script>',
                r'<dialog id="outdoorTempDialog"[\s\S]*?</dialog>'):
    html, count = re.subn(pattern, '', html)
    if count != 1:
        raise RuntimeError('Expected one retired weather component')
html = html.replace('</head>', '''<style id="rev165-naver-weather">
#outdoorTempBtn{text-decoration:none;text-align:center}
#outdoorTempBtn .naver-weather-label{font-size:12px;font-weight:900;line-height:1.3;color:#071d33;white-space:nowrap}
#outdoorTempBtn .naver-weather-open{font-size:9px;font-weight:700;line-height:1.2;color:#183d5d;white-space:nowrap}
#outdoorTempBtn:focus-visible{outline:3px solid #ffdf59;outline-offset:2px}
@media(max-width:350px){#outdoorTempBtn .naver-weather-label{font-size:11px}}
</style>
</head>''', 1)
if 'api.open-meteo.com' in html or 'id="outdoorTempValue"' in html:
    raise RuntimeError('Retired temperature estimation must not remain active')
html = html.replace('Rev.164', 'Rev.165').replace(registration, registration.replace('v=164', 'v=165'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev164-v1', '1560-timetable-rev165-v1').replace('REVISION="164"', 'REVISION="165"')
sw.write_text(text, encoding='utf-8')
