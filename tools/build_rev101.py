from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev100.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.100", "Rev.101")

bus_icon = r'''<svg class="rev101-route-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="4" y="3" width="16" height="16" rx="3"></rect><path d="M7 6h10v5H7z"></path><path d="M4 14h16"></path><circle cx="8" cy="16.5" r="1.2"></circle><circle cx="16" cy="16.5" r="1.2"></circle><path d="M7 19v2M17 19v2"></path></svg>'''

old_link = r'''      <a id="rev99-route-link" href="https://m.gbis.go.kr/busRouteLine/234000884" target="_blank" rel="noopener noreferrer" role="button" aria-label="1560A 노선 경로 지도 열기"><span class="rev100-route-top"><svg class="rev100-route-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="4" y="3" width="16" height="16" rx="3"></rect><path d="M7 6h10v5H7z"></path><path d="M4 14h16"></path><circle cx="8" cy="16.5" r="1.2"></circle><circle cx="16" cy="16.5" r="1.2"></circle><path d="M7 19v2M17 19v2"></path></svg><span>1560</span></span><span>노선경로</span></a>'''

new_links = f'''      <a id="rev101-route-a" class="rev101-route-link" href="https://m.gbis.go.kr/routeBusLocation/234000884" target="_blank" rel="noopener noreferrer" role="button" aria-label="1560A 실시간 버스위치 열기"><span class="rev101-route-top">{bus_icon}</span><span>1560A</span></a>
      <a id="rev101-route-b" class="rev101-route-link" href="https://m.gbis.go.kr/routeBusLocation/228000433" target="_blank" rel="noopener noreferrer" role="button" aria-label="1560B 실시간 버스위치 열기"><span class="rev101-route-top">{bus_icon}</span><span>1560B</span></a>'''

if old_link not in text:
    raise RuntimeError("Rev100 route-map link was not found")
text = text.replace(old_link, new_links, 1)

rev101_css = r'''

/* Rev101: separate 1560A and 1560B live-bus shortcuts. */
.info-bar{
  grid-template-columns:minmax(60px,.8fr) minmax(170px,1.8fr) minmax(60px,.8fr)!important;
}
#rev79-gyeonggi-card{
  grid-template-columns:minmax(42px,1fr) 44px 44px 54px!important;
}
.info-bar #rev79-gyeonggi-card .rev101-route-link{
  min-width:0!important;min-height:42px!important;margin:4px 0 4px 2px!important;
  padding:2px 1px!important;border:1px solid #1e4f8f!important;border-radius:9px!important;
  background:#2b66b1!important;color:#fff!important;
  box-shadow:0 3px 0 #194374,0 4px 8px rgba(29,72,126,.24)!important;
  display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;
  gap:1px!important;font-size:10px!important;font-weight:950!important;line-height:1!important;
  letter-spacing:-.35px!important;text-align:center!important;text-decoration:none!important;
}
.info-bar #rev101-route-a{border-color:#6ee78a!important}
.info-bar #rev101-route-b{border-color:#ffe074!important}
.info-bar #rev79-gyeonggi-card .rev101-route-link:active{
  transform:translateY(2px)!important;background:#235896!important;
  box-shadow:0 1px 0 #194374,0 2px 5px rgba(29,72,126,.22)!important;
}
.info-bar #rev79-gyeonggi-card .rev101-route-link:focus-visible{
  outline:3px solid #ffd85d!important;outline-offset:1px!important;
}
.info-bar #rev79-gyeonggi-card .rev101-route-top{
  display:flex;align-items:center;justify-content:center;line-height:1;
}
.info-bar #rev79-gyeonggi-card .rev101-route-icon{
  display:block;width:16px;height:16px;overflow:visible;
  fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;
}
.info-bar #rev79-gyeonggi-card .rev101-route-icon path:nth-of-type(1),
.info-bar #rev79-gyeonggi-card .rev101-route-icon circle{
  fill:currentColor;stroke:none;
}
@media(max-width:380px){
  .info-bar{grid-template-columns:minmax(60px,.7fr) minmax(170px,2fr) minmax(60px,.7fr)!important}
  #rev79-gyeonggi-card{grid-template-columns:minmax(42px,1fr) 40px 40px 48px!important}
  .info-bar #rev79-gyeonggi-card .rev101-route-link{font-size:9.5px!important;margin-left:1px!important}
  .info-bar #rev79-gyeonggi-card .rev101-route-icon{width:15px;height:15px}
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev101_css + "</style>", 1)

text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=100",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=101",{updateViaCache:"none"})',
    1,
)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev101-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="101";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
