from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev153.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=153",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.153' not in html:
    raise RuntimeError('Expected Rev153 input')

style = '''<style id="rev154-centered-instruments">
/* Equal side tracks keep both instruments on the header's center axis. */
.top-quick-links,.clock{
  grid-template-columns:minmax(0,1fr) 76px minmax(0,1fr)!important;
}
.clock #rev92-speedometer{width:100%!important;justify-self:center!important}
.clock #rev58-today-work.rev88-clock-calendar{min-width:0!important}
.clock #now{min-width:0;justify-self:end!important}
@media(max-width:350px){
  .top-quick-links,.clock{grid-template-columns:minmax(0,1fr) 68px minmax(0,1fr)!important}
}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.153', 'Rev.154').replace(registration, registration.replace('v=153', 'v=154'), 1)
index.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev153-v1', '1560-timetable-rev154-v1').replace('REVISION="153"', 'REVISION="154"')
sw.write_text(text, encoding='utf-8')
