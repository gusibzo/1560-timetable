from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev151.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=151",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.151' not in html:
    raise RuntimeError('Expected Rev151 input')

# Current public URLs obtained from GBIS search for each route. GBIS now
# decodes the path token; bare numeric route IDs no longer load the page.
routes = {
    '234000884': '2NzYyMzQwMDA4ODQ0NDkw4',
    '228000433': '5NDYzMjMyMjgwMDA0MzM2MDUzNg5',
}
for route_id, token in routes.items():
    before = f'https://m.gbis.go.kr/routeBusLocation/{route_id}'
    after = f'https://m.gbis.go.kr/routeBusLocation/{token}'
    if html.count(before) != 1:
        raise RuntimeError(f'Expected one live-bus link for {route_id}')
    html = html.replace(before, after, 1)

html = html.replace('Rev.151', 'Rev.152').replace(registration, registration.replace('v=151', 'v=152'), 1)
index.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev151-v1', '1560-timetable-rev152-v1').replace('REVISION="151"', 'REVISION="152"')
sw.write_text(text, encoding='utf-8')
