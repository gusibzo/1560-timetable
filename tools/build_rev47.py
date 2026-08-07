from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev46.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.46", "Rev.47")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=46",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=47",{updateViaCache:"none"})',
    1,
)

# TOPIS ignores the attempted total-map search query on some mobile browsers.
# Use the dedicated CCTV page instead, and copy the exact search term before leaving.
old_url = "https://topis.seoul.go.kr/map/openTotalMap.do?searchTxt=%EC%97%BC%EA%B3%A1%EC%82%AC%EA%B1%B0%EB%A6%AC"
new_url = "https://topis.seoul.go.kr/map/openCctvMap.do"
text = text.replace(f'href="{old_url}"', f'id="yeomgokCctvLink" href="{new_url}"', 1)
text = text.replace(
    '<strong>염곡사거리 CCTV</strong><small>구룡사 ↓ · 양재IC ↑ 방향 · 염곡사거리 검색</small>',
    '<strong>염곡사거리 CCTV</strong><small>검색어 “염곡사거리” 자동복사 · CCTV 전용화면</small>',
    1,
)
text = text.replace(
    '염곡사거리 버튼은 서울시 TOPIS에서 “염곡사거리” 검색 화면을 바로 엽니다. 검색 결과에서 염곡사거리를 선택한 뒤 파란 CCTV 아이콘을 누르면 구룡사 ↓ · 양재IC ↑ 방향 영상을 볼 수 있습니다.',
    '염곡사거리 버튼을 누르면 “염곡사거리”가 자동 복사되고 서울시 TOPIS CCTV 전용화면이 열립니다. CCTV 검색칸을 눌러 붙여넣기 → 검색 → 염곡사거리를 선택하면 구룡사 ↓ · 양재IC ↑ 방향 영상을 볼 수 있습니다.',
    1,
)

css = r'''
/* Rev47: clear two-step Yeomgok CCTV guidance. */
.traffic-choice.yeomgok small{color:#38634f!important}
.traffic-note strong{color:#176b43}
.yeomgok-copy-tip{
  margin:-2px 0 11px;
  padding:9px 11px;
  border-radius:12px;
  background:#fff7d6;
  border:1px solid #e7d589;
  color:#5d4b06;
  font-size:11.5px;
  font-weight:850;
  line-height:1.42;
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

needle = '</a>\n      <div class="traffic-note">염곡사거리 버튼을 누르면'
if needle in text:
    text = text.replace(
        needle,
        '</a>\n      <div class="yeomgok-copy-tip">📋 버튼을 누르면 <b>염곡사거리</b>가 휴대폰 클립보드에 복사됩니다. TOPIS에서 검색칸을 누른 뒤 <b>붙여넣기</b>만 하세요.</div>\n      <div class="traffic-note">염곡사거리 버튼을 누르면',
        1,
    )

script = r'''
<script>
(function(){
  const link=document.getElementById("yeomgokCctvLink");
  if(!link)return;

  function legacyCopy(text){
    const ta=document.createElement("textarea");
    ta.value=text;
    ta.setAttribute("readonly","");
    ta.style.position="fixed";
    ta.style.opacity="0";
    ta.style.pointerEvents="none";
    document.body.appendChild(ta);
    ta.select();
    try{document.execCommand("copy")}catch(_){}
    ta.remove();
  }

  link.addEventListener("click",function(event){
    event.preventDefault();
    const url=link.href;
    const word="염곡사거리";
    let moved=false;
    const go=function(){if(moved)return;moved=true;window.location.href=url};

    try{
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(word).then(go).catch(function(){legacyCopy(word);go()});
        setTimeout(go,450);
      }else{
        legacyCopy(word);go();
      }
    }catch(_){legacyCopy(word);go()}
  });
})();
</script>
'''
if "</body>" not in text:
    raise RuntimeError("closing body tag was not found")
text = text.replace("</body>", script + "\n</body>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev47-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="47";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
