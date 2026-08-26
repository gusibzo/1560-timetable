from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev81.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.81", "Rev.82")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=81",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=82",{updateViaCache:"none"})',
    1,
)

# Rev82: shorten the briefing heading and show only the next scheduled time.
old_title = '<span class="rev57-briefing-title">🚌 오늘 근무 브리핑</span>'
new_title = '<span class="rev57-briefing-title">🚌 오늘 운행 한눈보기</span>'
if text.count(old_title) != 1:
    raise RuntimeError("Rev81 briefing title was not found exactly once")
text = text.replace(old_title, new_title, 1)

old_next = 'if(nextEl)nextEl.textContent=next?rev57EventText(next):"오늘 운행 종료";'
new_next = 'if(nextEl)nextEl.textContent=next?next.time:"운행 종료";'
if text.count(old_next) != 1:
    raise RuntimeError("Rev81 next-departure text was not found exactly once")
text = text.replace(old_next, new_next, 1)

css = r'''
/* Rev82: driver glance layout — compact controls and three equal time cards. */
html,body{overflow-x:hidden!important}
body{padding-left:8px!important;padding-right:8px!important}
.wrap{width:100%!important;max-width:460px!important;min-width:0!important;overflow-x:clip!important}
.sticky-head{
  padding-bottom:7px!important;margin-bottom:8px!important;border-bottom-width:2px!important;
}
.plate{padding:11px 13px!important;border-radius:16px!important}
.route-no{font-size:36px!important}
.route-no small{font-size:14px!important}
.route-left{gap:5px!important}
.route-meta{font-size:10px!important;line-height:1.4!important}
.clock{margin-top:8px!important;padding-top:8px!important}
.info-bar{
  width:100%!important;min-width:0!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:6px!important;margin-top:7px!important;padding:6px!important;
}
.info-bar>a,.info-bar>button{
  min-width:0!important;min-height:50px!important;padding:8px 2px!important;
  border-radius:16px!important;font-size:12.5px!important;
}
#rev79-gyeonggi-card{
  width:100%!important;min-width:0!important;min-height:50px!important;
  grid-template-columns:minmax(0,1fr) 54px!important;
}
#rev79-gyeonggi-card #rev77-photo-thumb{
  min-width:0!important;min-height:50px!important;padding:4px!important;
}
#rev79-gyeonggi-card #rev77-photo-thumb img{width:56px!important;height:38px!important}
.info-bar #rev79-gyeonggi-link{
  min-width:0!important;min-height:42px!important;margin:4px!important;
  padding:3px 2px!important;border-radius:10px!important;font-size:13px!important;
}
.switch{
  width:100%!important;min-width:0!important;overflow:hidden!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;
  margin-top:8px!important;padding:4px!important;border-radius:16px!important;
}
.switch .ind{left:4px!important;top:4px!important;width:calc((100% - 8px)/3)!important;height:calc(100% - 8px)!important}
.seg{
  min-width:0!important;overflow:hidden!important;padding:9px 1px 7px!important;
  font-size:15px!important;line-height:1.08!important;white-space:nowrap!important;
}
.seg[data-day="sunday"]{font-size:11.5px!important;letter-spacing:-.7px!important}
.seg .cnt{font-size:10px!important;margin-top:4px!important}
.notice{
  width:100%!important;min-width:0!important;min-height:48px!important;overflow:hidden!important;
  grid-template-columns:minmax(0,1fr) auto minmax(0,1fr)!important;
  gap:6px!important;margin-top:8px!important;padding:7px 10px!important;
  border-radius:14px!important;font-size:15px!important;
}
.notice>span:first-child,.notice>b:last-child{
  min-width:0!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;
}
.notice .service-count{
  min-width:52px!important;padding:5px 9px!important;font-size:15px!important;
}
.rev57-briefing{
  width:100%!important;min-width:0!important;overflow:hidden!important;
  margin-top:8px!important;padding:10px!important;border-radius:17px!important;
}
.rev57-briefing-head{margin-bottom:8px!important;gap:6px!important}
.rev57-briefing-title{min-width:0!important;font-size:17px!important;line-height:1.1!important;white-space:nowrap!important}
.rev57-briefing-badge{padding:4px 7px!important;font-size:10px!important}
.rev57-briefing-grid{
  width:100%!important;min-width:0!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:6px!important;
}
.rev57-briefing-item{
  min-width:0!important;min-height:78px!important;overflow:hidden!important;
  align-items:center!important;justify-content:center!important;
  padding:8px 3px!important;text-align:center!important;border-radius:13px!important;
}
.rev74-current-card{background:linear-gradient(180deg,#293a30,#222c27)!important;border-color:rgba(126,232,139,.25)!important}
.rev74-counter-card{background:linear-gradient(180deg,#2b313a,#22272f)!important;border-color:rgba(255,255,255,.12)!important}
.rev74-next-card{background:linear-gradient(180deg,#3b3324,#2f2a21)!important;border-color:rgba(255,226,120,.25)!important}
.rev57-briefing-k{
  width:100%!important;color:#b8c0cb!important;font-size:10.5px!important;
  font-weight:950!important;line-height:1.05!important;text-align:center!important;white-space:nowrap!important;
}
#rev57-current,#rev57-next{
  display:block!important;width:100%!important;margin-top:7px!important;
  font-size:22px!important;line-height:1!important;letter-spacing:-.5px!important;
  white-space:nowrap!important;overflow:hidden!important;text-overflow:clip!important;text-align:center!important;
  font-variant-numeric:tabular-nums!important;
}
#rev57-current{color:#baff64!important}
#rev57-next{color:#ffe278!important}
.rev74-counter{
  width:100%!important;margin-top:7px!important;
  font-size:clamp(16px,5vw,22px)!important;line-height:1!important;letter-spacing:-1px!important;
}
.board{width:100%!important;max-width:100%!important;overflow:hidden!important}
.grid{width:100%!important;min-width:0!important;table-layout:fixed!important}
@media(max-width:380px){
  body{padding-left:6px!important;padding-right:6px!important}
  .plate{padding:10px 11px!important}
  .route-no{font-size:33px!important}
  .top-quick-links{gap:4px!important}
  .top-quick-links .gyeonggi-badge{padding:4px 7px!important;font-size:10px!important}
  .info-bar{gap:4px!important;padding:5px!important}
  .info-bar>a,.info-bar>button{font-size:11.5px!important}
  #rev79-gyeonggi-card{grid-template-columns:minmax(0,1fr) 48px!important}
  #rev79-gyeonggi-card #rev77-photo-thumb img{width:50px!important;height:35px!important}
  .info-bar #rev79-gyeonggi-link{font-size:11.5px!important;margin:4px 3px!important}
  .seg{font-size:14px!important}
  .seg[data-day="sunday"]{font-size:10.5px!important}
  .notice{padding:6px 8px!important;font-size:14px!important}
  .notice .service-count{min-width:48px!important;padding:5px 7px!important;font-size:14px!important}
  .rev57-briefing{padding:8px!important}
  .rev57-briefing-title{font-size:15px!important}
  .rev57-briefing-badge{font-size:9px!important}
  .rev57-briefing-grid{gap:5px!important}
  .rev57-briefing-item{min-height:74px!important;padding:7px 2px!important}
  .rev57-briefing-k{font-size:9.5px!important}
  #rev57-current,#rev57-next{font-size:19px!important}
  .rev74-counter{font-size:clamp(15.5px,4.9vw,18.5px)!important;letter-spacing:-1.2px!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev82-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="82";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
