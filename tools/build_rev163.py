from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev162.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=162",{updateViaCache:"none"})'
anchor = '   if(ci===4&&r.ext){'
if html.count(registration) != 1 or html.count(anchor) != 1:
    raise RuntimeError('Expected Rev162 timetable renderer')
# Add the note as a sibling so the live bus marker and time parsing stay intact.
html = html.replace(anchor, '''   if(r.no===9&&ci===1&&x==="10:30"){
    const note=document.createElement("small");
    note.className="first-fuel-note";note.textContent="첫주유";
    td.appendChild(note);
   }
''' + anchor, 1)
html = html.replace('</head>', '''<style id="rev163-first-fuel-style">
body .grid tbody td .first-fuel-note{display:block;margin-top:4px;color:#d71920!important;font-size:12px;font-weight:800;line-height:1.25;text-align:center;white-space:nowrap;text-shadow:none}
</style>
</head>''', 1)
html = html.replace('Rev.162', 'Rev.163').replace(registration, registration.replace('v=162', 'v=163'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev162-v1', '1560-timetable-rev163-v1').replace('REVISION="162"', 'REVISION="163"')
sw.write_text(text, encoding='utf-8')
