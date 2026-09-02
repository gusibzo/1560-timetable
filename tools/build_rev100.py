from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev99.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.99", "Rev.100")

old_link = r'''      <a id="rev99-route-link" href="https://m.gbis.go.kr/busRouteLine/234000884" target="_blank" rel="noopener noreferrer" role="button" aria-label="1560A 노선 경로 지도 열기"><span>1560</span><span>노선경로</span></a>'''

new_link = r'''      <a id="rev99-route-link" href="https://m.gbis.go.kr/busRouteLine/234000884" target="_blank" rel="noopener noreferrer" role="button" aria-label="1560A 노선 경로 지도 열기"><span class="rev100-route-top"><svg class="rev100-route-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="4" y="3" width="16" height="16" rx="3"></rect><path d="M7 6h10v5H7z"></path><path d="M4 14h16"></path><circle cx="8" cy="16.5" r="1.2"></circle><circle cx="16" cy="16.5" r="1.2"></circle><path d="M7 19v2M17 19v2"></path></svg><span>1560</span></span><span>노선경로</span></a>'''

if old_link not in text:
    raise RuntimeError("Rev99 1560 route-map link was not found")
text = text.replace(old_link, new_link, 1)

rev100_css = r'''

/* Rev100: always-visible bus pictogram on the 1560 route-map shortcut. */
.info-bar #rev99-route-link .rev100-route-top{
  display:flex;align-items:center;justify-content:center;gap:2px;
  font-size:12px;font-weight:950;line-height:1;
}
.info-bar #rev99-route-link .rev100-route-icon{
  display:block;width:18px;height:18px;flex:0 0 18px;overflow:visible;
  fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;
}
.info-bar #rev99-route-link .rev100-route-icon path:nth-of-type(1),
.info-bar #rev99-route-link .rev100-route-icon circle{
  fill:currentColor;stroke:none;
}
@media(max-width:380px){
  .info-bar #rev99-route-link .rev100-route-top{font-size:10.5px!important;gap:1px}
  .info-bar #rev99-route-link .rev100-route-icon{width:16px;height:16px;flex-basis:16px}
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev100_css + "</style>", 1)

text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=99",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=100",{updateViaCache:"none"})',
    1,
)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev100-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="100";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
