from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev44.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.44", "Rev.45")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=44",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=45",{updateViaCache:"none"})',
    1,
)

# Replace the single Yangjae CCTV link with a chooser button.
yangjae_url = "https://rtt.map.naver.com/end-traffic/bridges/cctv/web/home?cctvGroupId=17&channel=100&seq=10"
topis_url = "https://topis.seoul.go.kr/map/openCctvMap.do"
pattern = re.compile(
    r'<a href="https://rtt\.map\.naver\.com/end-traffic/bridges/cctv/web/home\?cctvGroupId=17&channel=100&seq=10"[^>]*>🛣️ 도로교통</a>'
)
replacement = '<button type="button" id="roadTrafficBtn" aria-label="양재와 염곡사거리 CCTV 선택">🛣️ 도로교통</button>'
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise RuntimeError("current road-traffic button was not found")

css = r'''
/* Rev45: road-traffic chooser for Yangjae and Yeomgok CCTV. */
.traffic-modal{
  position:fixed;inset:0;z-index:10050;display:none;align-items:center;justify-content:center;
  padding:18px;background:rgba(8,12,18,.58);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)
}
.traffic-modal.open{display:flex}
.traffic-card{
  width:min(420px,100%);border-radius:22px;background:#f5f7fa;color:#111;
  border:1px solid rgba(45,58,72,.22);box-shadow:0 22px 70px rgba(0,0,0,.34);overflow:hidden
}
.traffic-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 17px 12px;border-bottom:1px solid #d5dbe2}
.traffic-title{font-size:20px;font-weight:950;letter-spacing:-.5px}
.traffic-close{width:42px;height:42px;border:0;border-radius:13px;background:#e4e9ef;color:#242a31;font-size:26px;line-height:1;font-weight:900;cursor:pointer}
.traffic-body{padding:14px}
.traffic-choice{display:flex;align-items:center;gap:12px;text-decoration:none;color:#111;background:#fff;border:2px solid #9ca9b8;border-radius:18px;padding:14px 15px;margin-bottom:11px;box-shadow:0 5px 12px rgba(36,48,61,.10)}
.traffic-choice:active{transform:translateY(1px);box-shadow:0 2px 6px rgba(36,48,61,.12)}
.traffic-choice .ico{font-size:30px;line-height:1}
.traffic-choice .txt{display:flex;flex-direction:column;gap:3px;min-width:0}
.traffic-choice strong{font-size:18px;font-weight:950;line-height:1.1}
.traffic-choice small{font-size:12px;font-weight:800;color:#59636e;line-height:1.25}
.traffic-choice.yangjae{border-color:#7b9fc4}
.traffic-choice.yeomgok{border-color:#6aa98a}
.traffic-note{margin-top:3px;padding:10px 11px;border-radius:12px;background:#e9edf2;color:#4f5965;font-size:11.5px;font-weight:750;line-height:1.42}
@media(max-width:380px){.traffic-card{border-radius:18px}.traffic-head{padding:13px 14px 10px}.traffic-title{font-size:18px}.traffic-body{padding:11px}.traffic-choice{padding:12px}.traffic-choice strong{font-size:16px}}
'''
text = text.replace("</style>", css + "\n</style>", 1)

modal = f'''
<div class="traffic-modal" id="trafficModal" role="dialog" aria-modal="true" aria-labelledby="trafficTitle">
  <div class="traffic-card">
    <div class="traffic-head">
      <div class="traffic-title" id="trafficTitle">도로교통 CCTV</div>
      <button class="traffic-close" id="trafficClose" type="button" aria-label="닫기">×</button>
    </div>
    <div class="traffic-body">
      <a class="traffic-choice yangjae" href="{yangjae_url}" rel="noreferrer" referrerpolicy="no-referrer">
        <span class="ico">🚦</span><span class="txt"><strong>양재 CCTV</strong><small>경부고속도로 양재 화면 바로 열기</small></span>
      </a>
      <a class="traffic-choice yeomgok" href="{topis_url}" rel="noreferrer" referrerpolicy="no-referrer">
        <span class="ico">📹</span><span class="txt"><strong>염곡사거리 CCTV</strong><small>서울 TOPIS CCTV 지도에서 염곡사거리 카메라 확인</small></span>
      </a>
      <div class="traffic-note">염곡사거리 버튼은 서울시 TOPIS의 공식 CCTV 지도 화면을 엽니다. 지도에서 염곡사거리의 파란 CCTV 아이콘을 누르면 영상을 볼 수 있습니다.</div>
    </div>
  </div>
</div>
'''.strip()
if "</body>" not in text:
    raise RuntimeError("closing body tag was not found")
text = text.replace("</body>", modal + "\n</body>", 1)

script = r'''
<script>
(function(){
  const btn=document.getElementById("roadTrafficBtn");
  const modal=document.getElementById("trafficModal");
  const close=document.getElementById("trafficClose");
  if(!btn||!modal||!close)return;
  function openTraffic(){modal.classList.add("open");close.focus()}
  function closeTraffic(){modal.classList.remove("open");btn.focus()}
  btn.addEventListener("click",openTraffic);
  close.addEventListener("click",closeTraffic);
  modal.addEventListener("click",function(e){if(e.target===modal)closeTraffic()});
  modal.querySelectorAll("a").forEach(function(a){a.addEventListener("click",function(){modal.classList.remove("open")})});
  document.addEventListener("keydown",function(e){if(e.key==="Escape"&&modal.classList.contains("open"))closeTraffic()});
  window.addEventListener("pageshow",function(){modal.classList.remove("open")});
})();
</script>
'''
text = text.replace("</body>", script + "\n</body>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev45-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="45";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
