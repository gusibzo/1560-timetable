from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev108.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.108", "Rev.109")

links_pattern = re.compile(
    r'(?P<a><a id="rev101-route-a".*?</a>)\s*'
    r'(?P<b><a id="rev101-route-b".*?</a>)\s*'
    r'(?P<bus><a id="rev79-gyeonggi-link".*?</a>)',
    re.DOTALL,
)
match = links_pattern.search(text)
if not match:
    raise RuntimeError("Rev108 Gyeonggi Bus and 1560A/B links were not found")

grouped_links = (
    '<div id="rev109-gyeonggi-group" role="group" '
    'aria-label="경기버스와 1560A, 1560B 실시간 버스위치">\n'
    f'        {match.group("bus")}\n'
    '        <div class="rev109-route-row">\n'
    f'          {match.group("a")}\n'
    f'          {match.group("b")}\n'
    '        </div>\n'
    '      </div>'
)
text = text[: match.start()] + grouped_links + text[match.end() :]
text = text.replace(
    'aria-label="1560 사진, 노선 경로, 경기버스 바로가기"',
    'aria-label="1560 사진과 경기버스 바로가기"',
    1,
)

rev109_css = r'''

/* Rev109: place the 1560A and 1560B shortcuts inside the Gyeonggi Bus button. */
#rev79-gyeonggi-card{
  grid-template-columns:minmax(48px,1fr) minmax(104px,1.35fr)!important;
  gap:3px!important;
  align-items:stretch!important;
}
.info-bar #rev109-gyeonggi-group{
  min-width:0!important;
  min-height:42px!important;
  margin:4px!important;
  padding:3px!important;
  border:1px solid #1e4f8f!important;
  border-radius:10px!important;
  background:linear-gradient(180deg,#3474c4,#2863ad)!important;
  box-shadow:0 3px 0 #194374,0 4px 8px rgba(29,72,126,.24)!important;
  display:grid!important;
  grid-template-rows:17px minmax(20px,1fr)!important;
  gap:2px!important;
  overflow:hidden!important;
}
.info-bar #rev109-gyeonggi-group #rev79-gyeonggi-link{
  min-width:0!important;
  min-height:0!important;
  height:17px!important;
  margin:0!important;
  padding:0 2px!important;
  border:0!important;
  border-radius:5px!important;
  background:transparent!important;
  color:#fff!important;
  box-shadow:none!important;
  display:flex!important;
  flex-direction:row!important;
  align-items:center!important;
  justify-content:center!important;
  gap:0!important;
  font-size:11px!important;
  font-weight:950!important;
  line-height:1!important;
  letter-spacing:-.3px!important;
  white-space:nowrap!important;
}
.info-bar #rev109-gyeonggi-group #rev79-gyeonggi-link:active{
  transform:none!important;
  background:rgba(255,255,255,.16)!important;
  box-shadow:none!important;
}
.info-bar #rev109-gyeonggi-group .rev109-route-row{
  min-width:0!important;
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:3px!important;
}
.info-bar #rev109-gyeonggi-group .rev101-route-link{
  min-width:0!important;
  min-height:20px!important;
  margin:0!important;
  padding:1px!important;
  border:1px solid #79b8e8!important;
  border-radius:5px!important;
  background:linear-gradient(180deg,#eef8ff,#bfe2fa)!important;
  color:#124f7e!important;
  box-shadow:none!important;
  display:flex!important;
  flex-direction:row!important;
  align-items:center!important;
  justify-content:center!important;
  gap:1px!important;
  font-size:8.5px!important;
  font-weight:950!important;
  line-height:1!important;
  letter-spacing:-.45px!important;
  white-space:nowrap!important;
}
.info-bar #rev109-gyeonggi-group .rev101-route-link:active{
  transform:none!important;
  background:#9ecfee!important;
  box-shadow:none!important;
}
.info-bar #rev109-gyeonggi-group .rev101-route-icon{
  width:10px!important;
  height:10px!important;
  flex:0 0 10px!important;
}
.info-bar #rev109-gyeonggi-group a:focus-visible{
  outline:2px solid #ffd85d!important;
  outline-offset:-1px!important;
}
@media(max-width:380px){
  #rev79-gyeonggi-card{
    grid-template-columns:minmax(46px,1fr) minmax(96px,1.25fr)!important;
  }
  .info-bar #rev109-gyeonggi-group{margin:3px!important;padding:3px 2px!important}
  .info-bar #rev109-gyeonggi-group #rev79-gyeonggi-link{font-size:10.5px!important}
  .info-bar #rev109-gyeonggi-group .rev109-route-row{gap:2px!important}
  .info-bar #rev109-gyeonggi-group .rev101-route-link{font-size:8px!important;letter-spacing:-.55px!important}
  .info-bar #rev109-gyeonggi-group .rev101-route-icon{width:9px!important;height:9px!important;flex-basis:9px!important}
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev109_css + "</style>", 1)

old_registration = 'navigator.serviceWorker.register("./sw.js?v=108",{updateViaCache:"none"})'
new_registration = 'navigator.serviceWorker.register("./sw.js?v=109",{updateViaCache:"none"})'
if old_registration not in text:
    raise RuntimeError("Rev108 service worker registration was not found")
text = text.replace(old_registration, new_registration, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev109-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="109";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
