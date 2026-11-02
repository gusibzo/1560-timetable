"""Keep the alarm shortcut immediately above the current timetable bus."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev177.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
anchor = 'aria-label="알람 열기" title="알람">⏰<span id="alarmQuickTime"'
if html.count(anchor) != 1 or 'Rev.177' not in html:
    raise RuntimeError('Expected the Rev177 alarm shortcut')
html = html.replace(anchor, 'aria-label="알람 열기" title="알람"><span class="rev178-alarm-title">⏰ 알람</span><span id="alarmQuickTime"', 1)
style = '''<style id="rev178-alarm-above-bus">
/* A real link in the cell reserves space, so it never covers the bus or a time. */
#alarmQuick{
  position:relative!important;display:flex!important;flex-direction:column!important;
  align-items:center!important;justify-content:center!important;gap:1px!important;
  width:70px!important;min-width:70px!important;height:44px!important;min-height:44px!important;
  flex:0 0 70px!important;padding:3px 2px!important;box-sizing:border-box!important;
  border:2px solid #1e63d6!important;border-radius:12px!important;
  background:#e6f5ff!important;color:#123553!important;text-decoration:none!important;
  font:800 12px/1.2 system-ui,sans-serif!important;white-space:nowrap!important;
  text-shadow:none!important;box-shadow:0 2px 0 #12355333!important;
  touch-action:manipulation;
}
#alarmQuickTime{
  position:static!important;transform:none!important;padding:0!important;
  background:transparent!important;color:#123553!important;
  font:900 14px/1.15 ui-monospace,SFMono-Regular,Menlo,monospace!important;
}
.grid tbody td.rev178-has-alarm{padding-top:8px!important;padding-bottom:8px!important}
.grid tbody td.rev178-has-alarm > #alarmQuick{left:-7px!important;margin:0 auto 7px!important;z-index:8}
@media(max-width:380px){
  #alarmQuick{width:66px!important;min-width:66px!important;flex-basis:66px!important}
  .grid tbody td.rev178-has-alarm > #alarmQuick{left:-6px!important}
}
</style>
'''
script = '''<script id="rev178-alarm-above-bus">
(() => {
  const link = document.getElementById('alarmQuick');
  const home = document.querySelector('.side-tools');
  const rows = document.getElementById('rows');
  if (!link || !home || !rows) return;
  let previousCell = null;
  function placeAlarm() {
    const marker = rows.querySelector('td.next > .time, .next-ext');
    const cell = marker && marker.closest('td');
    if (previousCell && previousCell !== cell) previousCell.classList.remove('rev178-has-alarm');
    if (cell) {
      // Never put the link inside .time: the existing code reads its bus time.
      const before = marker.parentElement === cell ? marker : marker.closest('.ext');
      if (link.parentElement !== cell || link.nextElementSibling !== before) cell.insertBefore(link, before);
      if (!cell.classList.contains('rev178-has-alarm')) cell.classList.add('rev178-has-alarm');
    } else if (link.parentElement !== home) {
      // Another day's timetable (or before the first departure) has no live bus.
      home.appendChild(link);
    }
    previousCell = cell;
  }
  // Mutation delivery batches the existing per-second marker updates. Repeated
  // calls make no DOM changes once placed; the observer cannot feed itself.
  new MutationObserver(placeAlarm).observe(rows, {
    childList:true,subtree:true,attributes:true,attributeFilter:['class']
  });
  window.addEventListener('pageshow', placeAlarm);
  placeAlarm();
})();
</script>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('</body>', script + '</body>', 1)
html = html.replace('Rev.177', 'Rev.178').replace('sw.js?v=177', 'sw.js?v=178')
html = re.sub(r'(channel=\d+&amp;v=)177', r'\g<1>178', html)
html = html.replace("url.searchParams.set('v', '177');", "url.searchParams.set('v', '178');")
index.write_text(html, encoding='utf-8')
viewer = root / 'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=177', 'sw.js?v=178').replace('Rev.177', 'Rev.178'), encoding='utf-8')
sw = root / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('1560-timetable-rev177-v1', '1560-timetable-rev178-v1').replace('REVISION="177"', 'REVISION="178"'), encoding='utf-8')
