from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev148.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=148",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.148' not in html:
    raise RuntimeError('Expected Rev148 input')

style = '''<style id="rev149-compact-calendar">
/* Compact phone layout: keep all seven columns and up to six weeks visible. */
@media(max-width:560px){
  .calendar-card{width:min(420px,calc(100% - 28px));padding:10px;max-height:calc(100dvh - 30px)}
  .calendar-title{font-size:17px;line-height:1.2}
  .calendar-sub{font-size:10px;line-height:1.2}
  .calendar-nav{gap:4px}
  .calendar-nav button,.calendar-close,.calendar-today{min-width:32px;height:32px;padding:0 8px;font-size:13px}
  .calendar-close{font-size:20px}
  #rev58-work-panel{margin-top:7px;padding:8px;gap:0}
  .rev58-work-summary{font-size:12px;line-height:1.25}
  #rev58-work-count{font-size:clamp(11px,3vw,14px)!important;line-height:1.3;letter-spacing:-.3px!important}
  .rev60-work-start,.rev61-work-tip{font-size:11px;line-height:1.25;margin-top:3px}
  .calendar-week{gap:3px;margin-top:8px;font-size:12px}
  .calendar-grid{gap:3px;margin-top:4px;grid-template-columns:repeat(7,minmax(0,1fr))}
  .calendar-day{height:clamp(48px,calc((100vh - 330px)/6),68px);height:clamp(48px,calc((100dvh - 330px)/6),68px);min-height:0;padding:3px 2px 16px;border-radius:9px}
  .solar-row{min-height:17px}
  .solar-no{font-size:16px;line-height:1.05}
  .lunar{font-size:10px;line-height:1.1;margin-top:2px}
  .holiday-name,.event-name{font-size:10px;line-height:1.1;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .calendar-day.rev118-work-am::after,.calendar-day.rev118-work-pm::after{font-size:10px!important;padding:1px 2px!important}
  .calendar-legend{font-size:10px;gap:5px 8px;margin-top:6px}
  .rev118-legend-chip{font-size:10px;padding:2px 4px}
  .calendar-foot{margin-top:6px;gap:5px}
  .calendar-selected,.calendar-selected strong{font-size:11px;line-height:1.3;min-height:28px}
  .calendar-note{font-size:9px;line-height:1.2;margin-top:5px}
}
</style>
'''
html = html.replace('</head>', style + '</head>', 1)
html = html.replace('Rev.148', 'Rev.149').replace(registration, registration.replace('v=148', 'v=149'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev148-v1', '1560-timetable-rev149-v1').replace('REVISION="148"', 'REVISION="149"')
sw.write_text(text, encoding='utf-8')
