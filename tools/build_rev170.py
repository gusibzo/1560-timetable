"""Replace the model estimate and +3°C offset with KMA observations."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev169.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=169",{updateViaCache:"none"})'
if html.count(registration) != 1:
    raise RuntimeError('Expected Rev169 input')
link = '''<a id="outdoorTempBtn" href="https://www.weather.go.kr/w/index.do" target="_blank" rel="noopener noreferrer" aria-label="기상청 관측 기온 확인 중 · 날씨누리 열기, 새 창" title="기상청 관측 기온을 표시합니다."><span class="outdoor-temp-reading"><span id="outdoorWeatherIcon" aria-hidden="true">🌡️</span><strong id="outdoorTempValue">--°C</strong></span></a>'''
html, count = re.subn(r'<a id="outdoorTempBtn"[\s\S]*?</a>', lambda _: link, html)
if count != 1:
    raise RuntimeError('Expected one outdoor temperature tile')
script = Path(__file__).with_name('rev170_outdoor.js').read_text(encoding='utf-8')
html, count = re.subn(r'<script id="rev167-outdoor-script">[\s\S]*?</script>', lambda _: '<script id="rev170-outdoor-script">\n' + script + '\n</script>', html)
if count != 1:
    raise RuntimeError('Expected one previous weather controller')
html = html.replace('</head>', '''<style id="rev170-temperature-decimal">
#outdoorTempBtn #outdoorTempValue{font-size:15px;letter-spacing:-.4px;font-variant-numeric:tabular-nums}
#outdoorTempBtn .outdoor-temp-reading{gap:2px}
#outdoorTempBtn #outdoorWeatherIcon,#outdoorTempBtn #outdoorWeatherIcon svg{width:20px;flex-basis:20px}
</style>
</head>''', 1)
html = html.replace('Rev.169', 'Rev.170').replace(registration, registration.replace('v=169', 'v=170'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev169-v1', '1560-timetable-rev170-v1').replace('REVISION="169"', 'REVISION="170"')
anchor = '  // Keep the CCTV page separate from the timetable navigation cache.'
if text.count(anchor) != 1:
    raise RuntimeError('Expected service worker fetch handler')
text = text.replace(anchor, '''  // Weather is live data. Never retain each polling URL or reuse an offline
  // snapshot as a fresh temperature; the widget handles network failure.
  if(url.pathname===new URL("./weather/kma.json",self.registration.scope).pathname){
    event.respondWith(fetch(request,{cache:"no-store"}).catch(()=>Response.error()));
    return;
  }

''' + anchor, 1)
sw.write_text(text, encoding='utf-8')
