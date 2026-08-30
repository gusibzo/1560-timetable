from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev92.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.92", "Rev.93")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=92",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=93",{updateViaCache:"none"})',
    1,
)

old_gps_modal = r'''<div class="gps-modal" id="gpsModal" role="dialog" aria-modal="true" aria-labelledby="gpsTitle">
  <div class="gps-card">
    <div class="gps-head">
      <div>
        <div class="gps-title" id="gpsTitle">지도 · 속도계</div>
        <div class="gps-sub">위 화면처럼 쓸 수 있는 빠른 아이콘입니다. 현재 위치 좌표를 확인하거나 지도를 바로 열 수 있어요.</div>
      </div>
      <button class="gps-close" id="gpsClose" type="button" aria-label="닫기">×</button>
    </div>
    <div class="gps-grid">
      <div class="gps-box"><div class="num" id="gpsLat">--.--</div><span class="lab">위도</span></div>
      <div class="gps-box"><div class="num" id="gpsLon">--.--</div><span class="lab">경도</span></div>
    </div>
    <div class="gps-actions">
      <button class="locate" id="gpsLocate" type="button">📍 현재 위치 좌표</button>
      <a class="naver" id="naverMapOpen" href="nmap://map?appname=https%3A%2F%2Fgusibzo.github.io%2F1560-timetable%2F">🗺️ 네이버지도</a>
      <a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/run.jsp" rel="noopener noreferrer">🧭 T맵 실행</a>
      <a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" rel="noopener noreferrer">🚏 T맵 길찾기</a>
    </div>
    <div class="gps-msg" id="gpsMsg">버튼을 누르면 기기 위치 권한을 받아 현재 좌표를 표시합니다.</div>
    <div class="gps-note">※ 네이버지도 버튼을 누르면 이 창이 먼저 닫힙니다. 지도 앱에서 나오면 열린 시간표가 바로 보입니다.</div>
  </div>
</div>'''

new_gps_modal = r'''<div class="gps-modal" id="gpsModal" role="dialog" aria-modal="true" aria-labelledby="gpsTitle">
  <div class="gps-card">
    <div class="gps-head">
      <div>
        <div class="gps-title" id="gpsTitle">지도 바로가기</div>
        <div class="gps-sub">원하는 지도 앱을 바로 열 수 있습니다.</div>
      </div>
      <button class="gps-close" id="gpsClose" type="button" aria-label="닫기">×</button>
    </div>
    <div class="gps-actions rev93-map-actions">
      <a class="naver" id="naverMapOpen" href="nmap://map?appname=https%3A%2F%2Fgusibzo.github.io%2F1560-timetable%2F">🗺️ 네이버지도</a>
      <a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/run.jsp" rel="noopener noreferrer">🧭 T맵 실행</a>
      <a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" rel="noopener noreferrer">🚏 T맵 길찾기</a>
    </div>
    <div class="gps-note">※ 네이버지도 버튼을 누르면 이 창이 먼저 닫힙니다. 지도 앱에서 나오면 열린 시간표가 바로 보입니다.</div>
  </div>
</div>'''

if old_gps_modal not in text:
    raise RuntimeError("Rev92 GPS modal was not found")
text = text.replace(old_gps_modal, new_gps_modal, 1)

old_gps_script = r'''const gpsQuick=document.getElementById("gpsQuick");
const gpsModal=document.getElementById("gpsModal");
const gpsClose=document.getElementById("gpsClose");
const gpsLocate=document.getElementById("gpsLocate");
const gpsLat=document.getElementById("gpsLat");
const gpsLon=document.getElementById("gpsLon");
const gpsMsg=document.getElementById("gpsMsg");
function openGps(){gpsModal.classList.add("open");gpsQuick.classList.add("active");gpsClose.focus()}
function closeGps(){gpsModal.classList.remove("open");gpsQuick.classList.remove("active");gpsQuick.focus()}
function setGpsMessage(msg){gpsMsg.textContent=msg}
function updateCoords(lat,lon){gpsLat.textContent=Number(lat).toFixed(3);gpsLon.textContent=Number(lon).toFixed(3)}
function locateMe(){
 if(!navigator.geolocation){setGpsMessage("이 기기에서는 위치 기능을 지원하지 않습니다.");return}
 setGpsMessage("현재 위치를 확인하는 중입니다...");
 navigator.geolocation.getCurrentPosition(
  pos=>{
   const {latitude,longitude,accuracy}=pos.coords;
   updateCoords(latitude,longitude);
   setGpsMessage(`현재 좌표를 불러왔습니다. 정확도 약 ${Math.round(accuracy)}m`);
  },
  err=>{
   const map={1:"위치 권한이 거부되었습니다.",2:"현재 위치를 찾을 수 없습니다.",3:"위치 확인 시간이 초과되었습니다."};
   setGpsMessage(map[err.code]||"위치 정보를 가져오지 못했습니다.")
  },
  {enableHighAccuracy:true,timeout:10000,maximumAge:60000}
 )
}
gpsQuick.addEventListener("click",openGps);
gpsClose.addEventListener("click",closeGps);
gpsLocate.addEventListener("click",locateMe);
gpsModal.addEventListener("click",e=>{if(e.target===gpsModal)closeGps()});'''

new_gps_script = r'''const gpsQuick=document.getElementById("gpsQuick");
const gpsModal=document.getElementById("gpsModal");
const gpsClose=document.getElementById("gpsClose");
function openGps(){gpsModal.classList.add("open");gpsQuick.classList.add("active");gpsClose.focus()}
function closeGps(){gpsModal.classList.remove("open");gpsQuick.classList.remove("active");gpsQuick.focus()}
gpsQuick.addEventListener("click",openGps);
gpsClose.addEventListener("click",closeGps);
gpsModal.addEventListener("click",e=>{if(e.target===gpsModal)closeGps()});'''

if old_gps_script not in text:
    raise RuntimeError("Rev92 GPS coordinate script was not found")
text = text.replace(old_gps_script, new_gps_script, 1)

rev93_css = r'''

/* Rev93: simplified map launcher after removing coordinate readouts. */
.gps-actions.rev93-map-actions{
  grid-template-columns:1fr 1fr!important;
}
.gps-actions.rev93-map-actions .naver{
  grid-column:1/-1!important;
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev93_css + "</style>", 1)

old_speed_startup = r'''rev92EnsureSpeedometer();
setTimeout(rev92EnsureSpeedometer,120);
setInterval(rev92EnsureSpeedometer,1500);
window.addEventListener("pagehide",()=>rev92StopSpeedometer(true));'''

new_speed_startup = r'''let rev93SpeedAutoStarted=false;
function rev93AutoStartSpeedometer(){
 if(rev93SpeedAutoStarted)return;
 rev93SpeedAutoStarted=true;
 rev92EnsureSpeedometer();
 if(rev92SpeedWatch===null)rev92StartSpeedometer();
}

rev92EnsureSpeedometer();
setTimeout(rev93AutoStartSpeedometer,350);
setInterval(rev92EnsureSpeedometer,1500);
window.addEventListener("pageshow",()=>setTimeout(rev93AutoStartSpeedometer,250));
window.addEventListener("pagehide",()=>{
 rev92StopSpeedometer(true);
 rev93SpeedAutoStarted=false;
});'''

if old_speed_startup not in text:
    raise RuntimeError("Rev92 speedometer startup block was not found")
text = text.replace(old_speed_startup, new_speed_startup, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev93-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="93";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
