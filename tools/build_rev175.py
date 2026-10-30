"""Give the shared board shortcut immediate, reliable single-tap feedback."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev174.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
link = '<a id="busBoardBtn" href="https://bus1560-board.gusibzo.chatgpt.site/" aria-label="버스 게시판 열기">📋 게시판</a>'
if html.count(link) != 1:
    raise RuntimeError('Expected one board shortcut')
# Retain native navigation, including when JavaScript has not finished loading.
opening = '''<script id="rev175-board-opening">
(() => {
  const link = document.getElementById('busBoardBtn');
  const original = link.textContent;
  let opening = false, timer;
  function reset() {
    opening = false;
    clearTimeout(timer);
    link.textContent = original;
    link.removeAttribute('aria-busy');
  }
  link.addEventListener('click', event => {
    if (event.defaultPrevented || event.button > 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    if (opening) { event.preventDefault(); return; }
    opening = true;
    link.textContent = '📋 여는 중…';
    link.setAttribute('aria-busy', 'true');
    timer = setTimeout(reset, 12000);
    // The first click follows the actual href immediately; no popup or timer.
  });
  window.addEventListener('pageshow', reset);
})();
</script>'''
html = html.replace(link, link.replace(' aria-label=', ' target="_top" aria-label=') + opening, 1)
html = html.replace('</head>', '''<link rel="preconnect" href="https://bus1560-board.gusibzo.chatgpt.site">
<style id="rev175-board-tap-style">
.info-bar > #busBoardBtn{touch-action:manipulation!important;user-select:none;-webkit-user-select:none;position:relative;transform:none!important}
.info-bar > #busBoardBtn:active{transform:none!important}
</style>
</head>''', 1)
html = html.replace('Rev.174', 'Rev.175').replace('sw.js?v=174', 'sw.js?v=175')
html = re.sub(r'(channel=\d+&amp;v=)174', r'\g<1>175', html)
html = html.replace("url.searchParams.set('v', '174');", "url.searchParams.set('v', '175');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=174', 'sw.js?v=175').replace('Rev.174', 'Rev.175'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev174-v1', '1560-timetable-rev175-v1').replace('REVISION="174"', 'REVISION="175"'), encoding='utf-8')
