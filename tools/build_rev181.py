"""Align a square alarm icon with the bus at the timetable's right edge."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev180.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
html, count = re.subn(r'<script id="rev178-alarm-above-bus">[\s\S]*?</script>', '', html, count=1)
if count != 1 or 'Rev.180' not in html:
    raise RuntimeError('Expected the Rev180 bus alarm placement')
style = '''<style id="rev181-right-edge-alarm">
/* The narrow right rail keeps the clock clear of the fifth departure time. */
.board.rev181-alarm-docked{position:relative!important;padding-right:36px!important;box-sizing:border-box!important}
#alarmQuick{
  width:28px!important;min-width:28px!important;flex-basis:28px!important;
  height:28px!important;min-height:28px!important;font-size:22px!important;
}
#alarmQuick > .rev178-alarm-title{transform:none!important}
.board > #alarmQuick{
  position:absolute!important;z-index:8!important;
  top:var(--alarm-dock-top,0px)!important;right:4px!important;
  left:auto!important;bottom:auto!important;margin:0!important;transform:none!important;
}
#alarmQuick::after{inset:-8px}
</style>
'''
script = '''<script id="rev181-right-edge-alarm">
(() => {
  const link = document.getElementById('alarmQuick');
  const home = document.querySelector('.side-tools');
  const board = document.querySelector('.board');
  const rows = document.getElementById('rows');
  if (!link || !home || !board || !rows) return;
  let pending = false;
  function place() {
    pending = false;
    const marker = rows.querySelector('td.next > .time, .next-ext');
    if (!marker) {
      if (link.parentElement !== home) home.appendChild(link);
      if (board.classList.contains('rev181-alarm-docked')) board.classList.remove('rev181-alarm-docked');
      return;
    }
    if (!board.classList.contains('rev181-alarm-docked')) board.classList.add('rev181-alarm-docked');
    if (link.parentElement !== board) board.appendChild(link);
    const bus = marker.getBoundingClientRect();
    const top = bus.top - board.getBoundingClientRect().top + (bus.height - link.offsetHeight) / 2;
    const value = Math.round(top) + 'px';
    if (link.style.getPropertyValue('--alarm-dock-top') !== value) link.style.setProperty('--alarm-dock-top', value);
  }
  function schedule() {
    if (!pending) { pending = true; requestAnimationFrame(place); }
  }
  window.addEventListener('resize', schedule, {passive:true});
  window.addEventListener('pageshow', schedule);
  new MutationObserver(schedule).observe(rows, {
    childList:true,subtree:true,attributes:true,attributeFilter:['class']
  });
  if (typeof ResizeObserver !== 'undefined') new ResizeObserver(schedule).observe(rows);
  place();
})();
</script>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('</body>', script + '</body>', 1)
html = html.replace('Rev.180', 'Rev.181').replace('sw.js?v=180', 'sw.js?v=181')
html = re.sub(r'(channel=\d+&amp;v=)180', r'\g<1>181', html)
html = html.replace("url.searchParams.set('v', '180');", "url.searchParams.set('v', '181');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=180', 'sw.js?v=181').replace('Rev.180', 'Rev.181'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev180-v1', '1560-timetable-rev181-v1').replace('REVISION="180"', 'REVISION="181"'), encoding='utf-8')
