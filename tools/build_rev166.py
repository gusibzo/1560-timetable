from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev165.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=165",{updateViaCache:"none"})'
if html.count(registration) != 1:
    raise RuntimeError('Expected Rev165')
link = '''<a id="outdoorTempBtn" href="https://weather.naver.com/" target="_blank" rel="noopener noreferrer" aria-label="현재 위치 추정 기온 확인 중 · 네이버 날씨 열기, 새 창" title="현재 위치의 날씨 추정값입니다. 누르면 네이버 날씨가 열립니다."><span class="outdoor-temp-reading"><span id="outdoorWeatherIcon" aria-hidden="true">🌡️</span><strong id="outdoorTempValue">--°C</strong></span></a>'''
html, count = re.subn(r'<a id="outdoorTempBtn"[\s\S]*?</a>', lambda m: link, html)
if count != 1:
    raise RuntimeError('Expected one Naver weather tile')
js = Path(__file__).with_name('rev166_outdoor.js').read_text(encoding='utf-8')
html = html.replace('</body>', '<script id="rev166-outdoor-script">\n' + js + '\n</script>\n</body>', 1)
html = html.replace('</head>', '''<style id="rev166-weather-two-items">
#outdoorTempBtn .outdoor-temp-reading{gap:3px}
#outdoorTempBtn #outdoorTempValue{font-size:17px;line-height:1.2}
#outdoorTempBtn #outdoorWeatherIcon{font-size:22px}
@media(max-width:350px){#outdoorTempBtn #outdoorTempValue{font-size:16px}}
</style>
</head>''', 1)
html = html.replace('Rev.165', 'Rev.166').replace(registration, registration.replace('v=165', 'v=166'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev165-v1', '1560-timetable-rev166-v1').replace('REVISION="165"', 'REVISION="166"')
sw.write_text(text, encoding='utf-8')
