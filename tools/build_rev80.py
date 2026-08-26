from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev79.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.79", "Rev.80")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=79",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=80",{updateViaCache:"none"})',
    1,
)

old_link = '''<a id="rev79-gyeonggi-link" href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" aria-label="경기버스정보 열기"><span>경기</span><span>버스</span></a>'''
new_link = '''<a id="rev79-gyeonggi-link" href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" role="button" aria-label="경기버스정보 열기"><span>경기</span><span>버스</span></a>'''
if text.count(old_link) != 1:
    raise RuntimeError("Rev79 Gyeonggi Bus link was not found exactly once")
text = text.replace(old_link, new_link, 1)

css = r'''
/* Rev80: make the Gyeonggi Bus link look and feel like a distinct button. */
#rev79-gyeonggi-card{
  grid-template-columns:minmax(0,1fr) 62px!important;
}
.info-bar #rev79-gyeonggi-link{
  min-width:0!important;min-height:52px!important;margin:6px!important;padding:4px 3px!important;
  border:1px solid #1e4f8f!important;border-radius:12px!important;
  background:#2b66b1!important;color:#fff!important;
  box-shadow:0 3px 0 #194374,0 4px 9px rgba(29,72,126,.25)!important;
  font-size:15px!important;line-height:1.02!important;
  transition:transform .12s ease,box-shadow .12s ease,background .12s ease!important;
}
.info-bar #rev79-gyeonggi-link:active{
  transform:translateY(2px)!important;background:#235896!important;
  box-shadow:0 1px 0 #194374,0 2px 5px rgba(29,72,126,.22)!important;
}
.info-bar #rev79-gyeonggi-link:focus-visible{
  outline:3px solid #ffd85d!important;outline-offset:1px!important;
}
@media(max-width:380px){
  #rev79-gyeonggi-card{grid-template-columns:minmax(0,1fr) 54px!important}
  .info-bar #rev79-gyeonggi-link{min-height:52px!important;margin:6px 5px!important;font-size:13.5px!important}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev80-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="80";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
