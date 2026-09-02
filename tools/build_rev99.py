from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev98.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.98", "Rev.99")

old_card = r'''    <div id="rev79-gyeonggi-card" aria-label="경기버스와 1560 감사 이미지">
      <button type="button" id="rev77-photo-thumb" aria-haspopup="dialog" aria-controls="rev77-photo-modal" aria-label="1560 감사 이미지 크게 보기"><img id="rev77-photo-thumb-img" alt="1560 감사 이미지 미리보기"></button>
      <a id="rev79-gyeonggi-link" href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" role="button" aria-label="경기버스정보 열기"><span>경기</span><span>버스</span></a>
    </div>'''

new_card = r'''    <div id="rev79-gyeonggi-card" aria-label="1560 사진, 노선 경로, 경기버스 바로가기">
      <button type="button" id="rev77-photo-thumb" aria-haspopup="dialog" aria-controls="rev77-photo-modal" aria-label="1560 감사 이미지 크게 보기"><img id="rev77-photo-thumb-img" alt="1560 감사 이미지 미리보기"></button>
      <a id="rev99-route-link" href="https://m.gbis.go.kr/busRouteLine/234000884" target="_blank" rel="noopener noreferrer" role="button" aria-label="1560A 노선 경로 지도 열기"><span>1560</span><span>노선경로</span></a>
      <a id="rev79-gyeonggi-link" href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" role="button" aria-label="경기버스정보 열기"><span>경기</span><span>버스</span></a>
    </div>'''

if old_card not in text:
    raise RuntimeError("Rev98 Gyeonggi Bus card was not found")
text = text.replace(old_card, new_card, 1)

rev99_css = r'''

/* Rev99: direct 1560 route-map shortcut beside the Gyeonggi Bus button. */
.info-bar{
  grid-template-columns:minmax(74px,.86fr) minmax(150px,1.66fr) minmax(74px,.86fr)!important;
}
#rev79-gyeonggi-card{
  grid-template-columns:minmax(44px,1fr) 60px 54px!important;
}
.info-bar #rev99-route-link{
  min-width:0!important;min-height:42px!important;margin:4px 0 4px 2px!important;
  padding:3px 2px!important;border:1px solid #1e4f8f!important;border-radius:10px!important;
  background:#2b66b1!important;color:#fff!important;
  box-shadow:0 3px 0 #194374,0 4px 9px rgba(29,72,126,.25)!important;
  display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;
  font-size:11.5px!important;font-weight:950!important;line-height:1.04!important;letter-spacing:-.35px!important;
  text-align:center!important;text-decoration:none!important;
}
.info-bar #rev99-route-link:active{
  transform:translateY(2px)!important;background:#235896!important;
  box-shadow:0 1px 0 #194374,0 2px 5px rgba(29,72,126,.22)!important;
}
.info-bar #rev99-route-link:focus-visible{
  outline:3px solid #ffd85d!important;outline-offset:1px!important;
}
@media(max-width:380px){
  .info-bar{grid-template-columns:minmax(70px,.82fr) minmax(150px,1.76fr) minmax(70px,.82fr)!important}
  #rev79-gyeonggi-card{grid-template-columns:minmax(42px,1fr) 56px 48px!important}
  .info-bar #rev99-route-link{font-size:10.5px!important;margin-left:1px!important;letter-spacing:-.45px!important}
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev99_css + "</style>", 1)

text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=98",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=99",{updateViaCache:"none"})',
    1,
)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev99-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="99";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
