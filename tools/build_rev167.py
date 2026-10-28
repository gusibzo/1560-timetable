"""Apply the owner's requested +3°C display correction; keep the weather source."""
from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev166.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')

def replace_once(before, after):
    global html
    if html.count(before) != 1:
        raise RuntimeError('Expected one occurrence: ' + before)
    html = html.replace(before, after, 1)

replace_once('const text = Math.round(current.temperature_2m) +',
             'const displayOffsetC = 3; // User-requested display correction, not an observed temperature.\n      const text = Math.round(current.temperature_2m + displayOffsetC) +')
replace_once("const detail = '현재 위치 주변의 추정 기온 ' + current.temperature_2m.toFixed(1) + '°C'",
             "const detail = '사용자 보정 +3°C · 원자료 추정 기온 ' + current.temperature_2m.toFixed(1) + '°C · 보정 표시 ' + text")
replace_once("(ready ? '추정 기온 ' + text : detail)",
             "(ready ? '사용자 보정 +3°C 적용 기온 ' + text : detail)")
replace_once('현재 위치의 날씨 추정값입니다. 누르면 네이버 날씨가 열립니다.',
             '현재 위치 날씨 추정값에 사용자 보정 +3°C를 더해 표시합니다. 누르면 네이버 날씨가 열립니다.')
replace_once('id="rev166-outdoor-script"', 'id="rev167-outdoor-script"')
replace_once('navigator.serviceWorker.register("./sw.js?v=166",{updateViaCache:"none"})',
             'navigator.serviceWorker.register("./sw.js?v=167",{updateViaCache:"none"})')
html = html.replace('Rev.166', 'Rev.167')
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev166-v1', '1560-timetable-rev167-v1').replace('REVISION="166"', 'REVISION="167"')
sw.write_text(text, encoding='utf-8')
