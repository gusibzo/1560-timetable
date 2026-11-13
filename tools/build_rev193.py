"""Allow selecting a timetable departure and detecting a return to Kyung Hee."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev192.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
# Run after the timetable rows and the GPS distance function have been defined.
controller = re.search(r'<script id="rev189-trip-timer">[\s\S]+?</script>', html)
if not controller:
    raise RuntimeError('Expected one trip timer controller')
html = html[:controller.start()] + html[controller.end():]
html = html.replace('</body>', controller.group() + '\n</body>', 1)
old_slot = '''    if(next!==Infinity&&toMin(x)===next){td.classList.add("next");td.innerHTML=`<span class="time">${x}</span>`}
    else td.textContent=x;'''
new_slot = '''    if(next!==Infinity&&toMin(x)===next)td.classList.add("next");
    td.appendChild(departureSlot(x, state.day, `${r.no}번 ${ci+1}회`, true));'''
old_extension = '''    const e=document.createElement("span");e.className="ext";e.innerHTML=`+강남역 <b>${r.ext}</b>`;td.appendChild(e)'''
new_extension = '''    const e=document.createElement("span");e.className="ext";e.textContent="+강남역 ";
    e.appendChild(departureSlot(r.ext, state.day, `${r.no}번 강남역`, false));td.appendChild(e);'''
for original, updated in ((old_slot, new_slot), (old_extension, new_extension)):
    if html.count(original) != 1:
        raise RuntimeError('Expected one timetable time renderer')
    html = html.replace(original, updated)
slot_factory = '''function departureSlot(time, day, service, main) {
 const button=document.createElement("button");
 button.type="button";
 button.className=main?"time trip-slot":"trip-slot trip-slot-extra";
 button.textContent=time;
 button.dataset.tripTime=time;
 button.dataset.tripDay=day;
 button.setAttribute("aria-label",`${service} ${time} 출발 예약`);
 button.setAttribute("aria-pressed","false");
 return button;
}
'''
html = html.replace('function render(){\n const d=DATA[state.day]', slot_factory + 'function render(){\n const d=DATA[state.day]', 1)
html = html.replace('time.setAttribute("aria-label",`${time.textContent} ${time.dataset.route}`);',
                    'if(!time.dataset.tripTime)time.setAttribute("aria-label",`${time.textContent} ${time.dataset.route}`);')
html = html.replace('time.setAttribute("aria-label",`${labelTime} ${route}`);',
                    'if(!time.dataset.tripTime)time.setAttribute("aria-label",`${labelTime} ${route}`);')
css = Path(__file__).with_name('rev193_trip_reservation.css').read_text(encoding='utf-8')
html = html.replace('</head>', '<style id="rev193-trip-reservation">\n' + css + '</style>\n</head>', 1)
index.write_text(html, encoding='utf-8')

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.192', 'Rev.193').replace('sw.js?v=192', 'sw.js?v=193')
    html = re.sub(r'(channel=\d+&amp;v=)192', r'\g<1>193', html)
    html = html.replace("url.searchParams.set('v', '192');", "url.searchParams.set('v', '193');")
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev192-v1', '1560-timetable-rev193-v1')
sw.write_text(code.replace('REVISION="192"', 'REVISION="193"'), encoding='utf-8')
