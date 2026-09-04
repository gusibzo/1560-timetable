from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev107.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.107", "Rev.110")

main_links_pattern = re.compile(
    r'<a id="rev101-route-a".*?</a>\s*'
    r'<a id="rev101-route-b".*?</a>\s*'
    r'<a id="rev79-gyeonggi-link".*?</a>',
    re.DOTALL,
)
main_bus_button = (
    '<button type="button" id="rev79-gyeonggi-link" '
    'aria-haspopup="dialog" aria-controls="rev110-bus-modal" '
    'aria-label="경기버스 메뉴 열기"><span>경기</span><span>버스</span></button>'
)
text, main_link_count = main_links_pattern.subn(main_bus_button, text, count=1)
if main_link_count != 1:
    raise RuntimeError("Rev107 main 1560A/B and Gyeonggi Bus links were not found")
text = text.replace(
    'aria-label="1560 사진, 노선 경로, 경기버스 바로가기"',
    'aria-label="1560 사진과 경기버스 메뉴"',
    1,
)

bus_icon = r'''<svg class="rev110-bus-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="4" y="3" width="16" height="16" rx="3"></rect><path d="M7 6h10v5H7z"></path><path d="M4 14h16"></path><circle cx="8" cy="16.5" r="1.2"></circle><circle cx="16" cy="16.5" r="1.2"></circle><path d="M7 19v2M17 19v2"></path></svg>'''
bus_modal = f'''
<div id="rev110-bus-modal" hidden>
  <section id="rev110-bus-dialog" role="dialog" aria-modal="true" aria-labelledby="rev110-bus-title">
    <button type="button" id="rev110-bus-close" aria-label="경기버스 메뉴 닫기">×</button>
    <h2 id="rev110-bus-title">🚌 경기버스</h2>
    <p>원하시는 노선을 눌러주세요(^_^)</p>
    <div class="rev110-bus-routes">
      <a href="https://m.gbis.go.kr/routeBusLocation/234000884" target="_blank" rel="noopener noreferrer" aria-label="1560A 실시간 버스위치 열기">{bus_icon}<strong>1560A</strong><span>실시간 위치</span></a>
      <a href="https://m.gbis.go.kr/routeBusLocation/228000433" target="_blank" rel="noopener noreferrer" aria-label="1560B 실시간 버스위치 열기">{bus_icon}<strong>1560B</strong><span>실시간 위치</span></a>
    </div>
    <a id="rev110-bus-search" href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer">경기버스 전체 검색</a>
  </section>
</div>
'''
if "</body>" not in text:
    raise RuntimeError("Body closing tag is missing")
text = text.replace("</body>", bus_modal + "</body>", 1)

rev110_css = r'''

/* Rev108 carried forward: keep the remaining quick buttons below the timetable. */
.side-tools{
  position:relative!important;z-index:auto!important;top:auto!important;right:auto!important;bottom:auto!important;
  width:min(460px,calc(100% - 20px))!important;
  margin:12px auto calc(18px + env(safe-area-inset-bottom))!important;
  padding:0 6px!important;display:flex!important;flex-direction:row!important;
  align-items:center!important;justify-content:flex-end!important;gap:10px!important;
}
.side-tool{width:43px!important;height:43px!important;flex:0 0 43px!important}
#quickCalendar{display:none!important}

/* Rev110: restore the compact main layout and open A/B inside the Gyeonggi Bus menu. */
#rev79-gyeonggi-card{
  grid-template-columns:minmax(0,1fr) 54px!important;
  gap:0!important;
}
.info-bar #rev79-gyeonggi-link{
  -webkit-appearance:none!important;appearance:none!important;
  font-family:inherit!important;cursor:pointer!important;
}
#rev110-bus-modal{
  position:fixed;inset:0;z-index:25000;
  padding:18px;display:flex;align-items:center;justify-content:center;
  background:rgba(8,12,19,.78);backdrop-filter:blur(3px);
}
#rev110-bus-modal[hidden]{display:none!important}
#rev110-bus-dialog{
  position:relative;width:min(100%,360px);padding:22px 18px 18px;
  border:2px solid #78baf0;border-radius:22px;
  background:linear-gradient(180deg,#3474c4,#22569b);color:#fff;
  box-shadow:0 18px 55px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.25);
  text-align:center;
}
#rev110-bus-title{margin:0;font-size:25px;line-height:1.1;font-weight:950}
#rev110-bus-dialog>p{margin:8px 0 16px;font-size:14px;font-weight:800;color:#eaf5ff}
#rev110-bus-close{
  position:absolute;top:9px;right:9px;width:38px;height:38px;padding:0;border:0;border-radius:50%;
  background:rgba(10,28,55,.7);color:#fff;font:900 28px/1 inherit;cursor:pointer;
}
.rev110-bus-routes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.rev110-bus-routes>a{
  min-width:0;min-height:104px;padding:12px 5px 10px;border:2px solid #78baf0;border-radius:16px;
  background:linear-gradient(180deg,#eef8ff,#b9dff8);color:#124f7e;text-decoration:none;
  box-shadow:0 4px 0 #17467b;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;
}
.rev110-bus-routes>a:active{transform:translateY(3px);box-shadow:0 1px 0 #17467b}
.rev110-bus-routes strong{font-size:24px;line-height:1;font-weight:950}
.rev110-bus-routes span{font-size:12px;font-weight:850}
.rev110-bus-icon{width:30px;height:30px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.rev110-bus-icon path:nth-of-type(1),.rev110-bus-icon circle{fill:currentColor;stroke:none}
#rev110-bus-search{
  min-height:46px;margin-top:14px;padding:10px 8px;border:1px solid rgba(255,255,255,.75);border-radius:12px;
  display:flex;align-items:center;justify-content:center;background:rgba(9,36,75,.42);color:#fff;
  font-size:15px;font-weight:950;text-decoration:none;
}
#rev110-bus-dialog a:focus-visible,#rev110-bus-close:focus-visible{outline:3px solid #ffd85d;outline-offset:2px}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev110_css + "</style>", 1)

rev110_js = r'''
<script>
(function(){
  const openButton=document.getElementById("rev79-gyeonggi-link");
  const modal=document.getElementById("rev110-bus-modal");
  const closeButton=document.getElementById("rev110-bus-close");
  if(!openButton||!modal||!closeButton)return;
  function openMenu(){modal.hidden=false;document.body.style.overflow="hidden";closeButton.focus()}
  function closeMenu(){modal.hidden=true;document.body.style.overflow="";openButton.focus()}
  openButton.addEventListener("click",openMenu);
  closeButton.addEventListener("click",closeMenu);
  modal.addEventListener("click",function(event){if(event.target===modal)closeMenu()});
  document.addEventListener("keydown",function(event){if(event.key==="Escape"&&!modal.hidden)closeMenu()});
})();
</script>
'''
text = text.replace("</body>", rev110_js + "</body>", 1)

new_registration = 'navigator.serviceWorker.register("./sw.js?v=110",{updateViaCache:"none"})'
registration_pattern = re.compile(
    r'navigator\.serviceWorker\.register\("\./sw\.js\?v=107(?:-5)?",'
    r'\{updateViaCache:"none"\}\)'
)
text, registration_count = registration_pattern.subn(new_registration, text, count=1)
if registration_count != 1:
    raise RuntimeError("Rev107 service worker registration was not found")
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev110-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="110";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
