"""Float the alarm above nearby numbers without narrowing the timetable."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev181.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
old_position = "    const top = bus.top - board.getBoundingClientRect().top + (bus.height - link.offsetHeight) / 2;"
if html.count(old_position) != 1 or 'Rev.181' not in html:
    raise RuntimeError('Expected the Rev181 alarm positioning')
helpers = '''  // Pick the nearest clear space above the bus's center. Text rectangles
  // include extension times, so the floating clock cannot cover those either.
  function clearTop(preferred, height, blocks) {
    const candidates = [preferred];
    for (const block of blocks) candidates.push(block.top - height - 4, block.bottom + 4);
    const safe = candidates.filter(top => blocks.every(block => top + height <= block.top - 4 || top >= block.bottom + 4));
    safe.sort((a, b) => Math.abs(a - preferred) - Math.abs(b - preferred) || a - b);
    return safe.length ? safe[0] : preferred;
  }
  function numberRects(icon) {
    const blocks = [];
    const walker = document.createTreeWalker(rows, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    let node;
    while ((node = walker.nextNode())) {
      if (!/\\d/.test(node.textContent)) continue;
      range.selectNodeContents(node);
      for (const rect of range.getClientRects()) {
        if (rect.width && rect.height && rect.left < icon.right + 4 && rect.right > icon.left - 4) blocks.push(rect);
      }
    }
    return blocks;
  }
'''
html = html.replace('  function place() {', helpers + '  function place() {', 1)
new_position = '''    const box = link.getBoundingClientRect();
    const icon = link.querySelector('.rev178-alarm-title').getBoundingClientRect();
    const preferred = bus.top + (bus.height - icon.height) / 2 - 24;
    const top = clearTop(preferred, icon.height, numberRects(icon)) - (icon.top - box.top) - board.getBoundingClientRect().top;'''
html = html.replace(old_position, new_position, 1)
html = html.replace('<script id="rev181-right-edge-alarm">', '<script id="rev182-floating-alarm">', 1)
style = '''<style id="rev182-floating-alarm">
/* Restore the full table width; the small clock overlays only clear space. */
.board.rev181-alarm-docked{padding-right:0!important;overflow:visible!important}
.board > #alarmQuick{filter:drop-shadow(0 1px 1px #fff)}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.181', 'Rev.182').replace('sw.js?v=181', 'sw.js?v=182')
html = re.sub(r'(channel=\d+&amp;v=)181', r'\g<1>182', html)
html = html.replace("url.searchParams.set('v', '181');", "url.searchParams.set('v', '182');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=181', 'sw.js?v=182').replace('Rev.181', 'Rev.182'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev181-v1', '1560-timetable-rev182-v1').replace('REVISION="181"', 'REVISION="182"'), encoding='utf-8')
