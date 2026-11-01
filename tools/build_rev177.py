"""Add a Samsung-clock style alarm page (alarm.html) and a side shortcut to it."""
from pathlib import Path
import re
import runpy
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
base=Path(__file__).with_name('build_rev176.py')
old=sys.argv[:]
try:
    sys.argv=[str(base),str(root)]
    runpy.run_path(str(base),run_name='__main__')
finally:
    sys.argv=old

alarm=Path(__file__).with_name('rev177_alarm.html').read_text(encoding='utf-8')
(root/'alarm.html').write_text(alarm,encoding='utf-8')

index=root/'index.html'
html=index.read_text(encoding='utf-8')
anchor='<button class="side-tool" id="gpsQuick" type="button" aria-label="지도와 속도계 기능 열기" title="지도·속도계">🧭</button>'
if html.count(anchor)!=1 or 'Rev.176' not in html:
    raise RuntimeError('Expected Rev176 side tools')
shortcut=('<a class="side-tool" id="alarmQuick" href="./alarm.html" aria-label="알람 열기" title="알람">⏰'
          '<span id="alarmQuickTime" aria-hidden="true"></span></a>')
html=html.replace(anchor,anchor+'\n    '+shortcut,1)
style='''<style id="rev177-alarm-shortcut">
.side-tools>#alarmQuick{position:relative;text-decoration:none;line-height:1}
#alarmQuickTime{position:absolute;left:50%;bottom:-7px;transform:translateX(-50%);padding:1px 4px;border-radius:6px;background:#ffb400;color:#1b1300;font:800 10px/1.25 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:nowrap;pointer-events:none}
#alarmQuickTime:empty{display:none}
</style>
'''
script='''<script id="rev177-alarm-shortcut-time">
(() => {
  const label = document.getElementById('alarmQuickTime');
  const link = document.getElementById('alarmQuick');
  if (!label || !link) return;
  function nextAlarm(now) {
    let data;
    try { data = JSON.parse(localStorage.getItem('bus1560.alarm.v1') || 'null'); } catch (_) { return null; }
    if (!data || !Array.isArray(data.alarms)) return null;
    let best = null;
    for (const a of data.alarms) {
      if (!a.enabled) continue;
      let t = null;
      if (a.snoozeUntil && a.snoozeUntil > now) t = a.snoozeUntil;
      else if (a.date) {
        const [y, m, d] = String(a.date).split('-').map(Number);
        const c = new Date(y, m - 1, d, a.h, a.m).getTime();
        if (c > now) t = c;
      } else {
        const n = new Date(now);
        for (let i = 0; i <= 8 && t === null; i++) {
          const c = new Date(n.getFullYear(), n.getMonth(), n.getDate() + i, a.h, a.m);
          if (c.getTime() > now && (!a.days || !a.days.length || a.days.includes(c.getDay()))) t = c.getTime();
        }
      }
      if (t !== null && (best === null || t < best)) best = t;
    }
    return best;
  }
  function update() {
    const t = nextAlarm(Date.now());
    if (t === null) { label.textContent = ''; link.setAttribute('aria-label', '알람 열기'); return; }
    const d = new Date(t), hm = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
    label.textContent = hm;
    link.setAttribute('aria-label', '알람 열기, 다음 알람 ' + hm);
  }
  update();
  setInterval(update, 30000);
  window.addEventListener('pageshow', update);
  window.addEventListener('storage', update);
})();
</script>
'''
html=html.replace('</head>',style+'</head>',1)
html=html.replace('</body>',script+'</body>',1)
html=html.replace('Rev.176','Rev.177').replace('sw.js?v=176','sw.js?v=177')
html=re.sub(r'(channel=\d+&amp;v=)176',r'\g<1>177',html)
html=html.replace("url.searchParams.set('v', '176');","url.searchParams.set('v', '177');")
index.write_text(html,encoding='utf-8')

viewer=root/'cctv.html'
viewer.write_text(viewer.read_text(encoding='utf-8').replace('sw.js?v=176','sw.js?v=177').replace('Rev.176','Rev.177'),encoding='utf-8')

sw=root/'sw.js'
code=sw.read_text(encoding='utf-8').replace('1560-timetable-rev176-v1','1560-timetable-rev177-v1').replace('REVISION="176"','REVISION="177"')
code+='''
/* Rev.177: tapping an alarm notification returns to the alarm page. */
self.addEventListener("notificationclick",event=>{
  event.notification.close();
  event.waitUntil((async()=>{
    const windows=await self.clients.matchAll({type:"window",includeUncontrolled:true});
    for(const client of windows){
      if(new URL(client.url).pathname.endsWith("/alarm.html")&&"focus" in client)return client.focus();
    }
    if(self.clients.openWindow)return self.clients.openWindow(new URL("./alarm.html",self.registration.scope).href);
  })());
});
'''
sw.write_text(code,encoding='utf-8')
