from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev160.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=160",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.160' not in html:
    raise RuntimeError('Expected Rev160 input')

viewer = root / 'cctv.html'
page = viewer.read_text(encoding='utf-8')
anchor = '<header><a href="./index.html">'
if page.count(anchor) != 1:
    raise RuntimeError('Expected timetable return link')
page = page.replace(anchor, '<header><a id="cctvTimetable" href="./index.html">', 1)
anchor = '<main class="video-window">'
if page.count(anchor) != 1:
    raise RuntimeError('Expected CCTV video window')
# The provider's close button goes back through the iframe's camera history.
# Put our direct timetable link over that corner, outside the provider iframe.
page = page.replace(anchor, anchor + '<a id="cctvClose" href="./index.html" aria-label="CCTV 닫고 시간표로 돌아가기">×</a>', 1)
style = '''<style id="rev161-cctv-close-style">
#cctvClose{position:absolute;z-index:2;top:0;right:0;width:84px;height:84px;display:grid;place-items:center;background:#0f0f0f;color:#fff;text-decoration:none;font:400 52px/1 system-ui,sans-serif;touch-action:manipulation}
#cctvClose:focus-visible{outline:3px solid #ffdf59;outline-offset:-5px}
</style>
'''
page = page.replace('</head>', style + '</head>', 1)
script = '''<script id="rev161-cctv-exit">
(() => {
  const timetable = new URL('./index.html', location.href).href;
  for (const id of ['cctvClose', 'cctvTimetable']) {
    const link = document.getElementById(id);
    link.addEventListener('click', event => {
      event.preventDefault();
      location.replace(timetable);
    });
  }
})();
</script>
'''
page = page.replace('</body>', script + '</body>', 1)
viewer.write_text(page, encoding='utf-8')
html = html.replace('Rev.160', 'Rev.161').replace(registration, registration.replace('v=160', 'v=161'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev160-v1', '1560-timetable-rev161-v1').replace('REVISION="160"', 'REVISION="161"')
sw.write_text(text, encoding='utf-8')
