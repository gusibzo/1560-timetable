from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev91.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.91", "Rev.92")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=91",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=92",{updateViaCache:"none"})',
    1,
)

rev92_css = r'''

/* Rev92: compact GPS speedometer beside the work-calendar button. */
.clock #rev92-speedometer{
  -webkit-appearance:none!important;
  appearance:none!important;
  position:relative!important;
  flex:0 0 64px!important;
  min-width:64px!important;
  min-height:36px!important;
  margin:0!important;
  padding:5px 5px 4px!important;
  border:1px solid rgba(255,255,255,.22)!important;
  border-radius:10px!important;
  background:linear-gradient(180deg,#3d4652,#252c35)!important;
  color:#fff!important;
  font-family:inherit!important;
  font-weight:950!important;
  line-height:1!important;
  cursor:pointer!important;
  box-shadow:0 2px 0 rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.12)!important;
  display:flex!important;
  align-items:baseline!important;
  justify-content:center!important;
  gap:2px!important;
  white-space:nowrap!important;
}
.clock #rev92-speedometer .rev92-speed-number{
  color:#8dff65!important;
  font:950 18px/1 ui-monospace,SFMono-Regular,Menlo,monospace!important;
  font-variant-numeric:tabular-nums!important;
}
.clock #rev92-speedometer .rev92-speed-unit{
  color:#dce3ea!important;
  font:900 8px/1 inherit!important;
}
.clock #rev92-speedometer.tracking{
  border-color:rgba(141,255,101,.82)!important;
  box-shadow:0 2px 0 rgba(0,0,0,.28),0 0 0 2px rgba(141,255,101,.18),inset 0 1px 0 rgba(255,255,255,.12)!important;
}
.clock #rev92-speedometer.speed-error .rev92-speed-number{color:#ff867f!important;font-size:13px!important}
@media(max-width:380px){
  .clock #rev92-speedometer{flex-basis:58px!important;min-width:58px!important;padding-left:3px!important;padding-right:3px!important}
  .clock #rev92-speedometer .rev92-speed-number{font-size:16px!important}
  .clock #rev92-speedometer .rev92-speed-unit{font-size:7px!important}
  .clock #rev58-today-work.rev88-clock-calendar,
  .clock #rev58-today-work.rev88-clock-calendar.checked{font-size:10px!important;padding-left:5px!important;padding-right:5px!important}
  #now{font-size:clamp(18px,5.7vw,22px)!important;letter-spacing:.2px!important}
}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", rev92_css + "</style>", 1)

rev92_script = r'''

/* Rev92: on-device GPS speedometer. No location data leaves the phone. */
let rev92SpeedWatch=null;
let rev92PreviousPosition=null;
let rev92SpeedSamples=[];

function rev92EnsureSpeedometer(){
 const clock=document.querySelector(".clock");
 const calendar=document.getElementById("rev58-today-work");
 const now=document.getElementById("now");
 if(!clock||!now)return null;
 let btn=document.getElementById("rev92-speedometer");
 if(!btn){
  btn=document.createElement("button");
  btn.type="button";
  btn.id="rev92-speedometer";
  btn.title="GPS 속도계 시작 · 위치 정보는 휴대폰 안에서만 사용됩니다";
  btn.innerHTML='<span class="rev92-speed-number">0</span><span class="rev92-speed-unit">km/h</span>';
  btn.setAttribute("aria-label","GPS 속도계 시작 · 현재 속도 0 km/h");
  btn.addEventListener("click",rev92ToggleSpeedometer);
 }
 if(btn.parentElement!==clock)clock.insertBefore(btn,now);
 if(calendar&&calendar.parentElement===clock&&calendar.nextElementSibling!==btn)calendar.insertAdjacentElement("afterend",btn);
 return btn;
}

function rev92DistanceMetres(a,b){
 const rad=Math.PI/180;
 const lat1=a.latitude*rad,lat2=b.latitude*rad;
 const dLat=(b.latitude-a.latitude)*rad,dLon=(b.longitude-a.longitude)*rad;
 const h=Math.sin(dLat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2;
 return 6371000*2*Math.atan2(Math.sqrt(h),Math.sqrt(1-h));
}

function rev92ShowSpeed(value,label){
 const btn=rev92EnsureSpeedometer();
 if(!btn)return;
 const number=btn.querySelector(".rev92-speed-number");
 const unit=btn.querySelector(".rev92-speed-unit");
 if(label){
  number.textContent=label;
  unit.textContent="";
  btn.classList.add("speed-error");
 }else{
  const rounded=Math.max(0,Math.min(199,Math.round(value||0)));
  number.textContent=String(rounded);
  unit.textContent="km/h";
  btn.classList.remove("speed-error");
  btn.setAttribute("aria-label",`GPS 속도계 측정 중 · 현재 속도 ${rounded} km/h · 누르면 정지`);
 }
}

function rev92OnSpeedPosition(position){
 const coords=position.coords;
 const timestamp=position.timestamp||Date.now();
 let kmh=Number.isFinite(coords.speed)&&coords.speed>=0?coords.speed*3.6:null;
 if(kmh===null&&rev92PreviousPosition){
  const elapsed=(timestamp-rev92PreviousPosition.timestamp)/1000;
  if(elapsed>=.7&&elapsed<=15){
   const metres=rev92DistanceMetres(rev92PreviousPosition.coords,coords);
   const noise=Math.max(3,Math.min(20,(coords.accuracy||0)*.35));
   kmh=metres<=noise?0:(metres/elapsed)*3.6;
  }
 }
 rev92PreviousPosition={coords:{latitude:coords.latitude,longitude:coords.longitude},timestamp};
 if(kmh===null)return;
 kmh=Math.max(0,Math.min(199,kmh));
 rev92SpeedSamples.push(kmh);
 if(rev92SpeedSamples.length>3)rev92SpeedSamples.shift();
 const smoothed=rev92SpeedSamples.reduce((sum,n)=>sum+n,0)/rev92SpeedSamples.length;
 rev92ShowSpeed(smoothed);
}

function rev92StopSpeedometer(reset=true){
 if(rev92SpeedWatch!==null&&navigator.geolocation)navigator.geolocation.clearWatch(rev92SpeedWatch);
 rev92SpeedWatch=null;
 rev92PreviousPosition=null;
 rev92SpeedSamples=[];
 const btn=rev92EnsureSpeedometer();
 if(!btn)return;
 btn.classList.remove("tracking","speed-error");
 btn.title="GPS 속도계 시작 · 위치 정보는 휴대폰 안에서만 사용됩니다";
 btn.setAttribute("aria-label","GPS 속도계 시작 · 현재 속도 0 km/h");
 if(reset)rev92ShowSpeed(0);
}

function rev92StartSpeedometer(){
 const btn=rev92EnsureSpeedometer();
 if(!btn)return;
 if(!navigator.geolocation){
  rev92ShowSpeed(0,"지원X");
  btn.setAttribute("aria-label","이 기기에서는 GPS 속도계를 지원하지 않습니다");
  return;
 }
 btn.classList.add("tracking");
 btn.classList.remove("speed-error");
 btn.title="GPS 속도계 측정 중 · 누르면 정지";
 rev92ShowSpeed(0);
 rev92SpeedWatch=navigator.geolocation.watchPosition(
  rev92OnSpeedPosition,
  error=>{
   const labels={1:"권한X",2:"신호X",3:"대기"};
   rev92ShowSpeed(0,labels[error.code]||"오류");
   btn.setAttribute("aria-label",error.code===1?"위치 권한이 필요합니다 · 눌러서 다시 시도":"GPS 신호를 기다리는 중입니다");
   if(error.code===1){
    if(rev92SpeedWatch!==null)navigator.geolocation.clearWatch(rev92SpeedWatch);
    rev92SpeedWatch=null;
    rev92PreviousPosition=null;
    rev92SpeedSamples=[];
    btn.classList.remove("tracking");
    btn.title="위치 권한이 필요합니다 · 눌러서 다시 시도";
   }
  },
  {enableHighAccuracy:true,maximumAge:1000,timeout:15000}
 );
}

function rev92ToggleSpeedometer(){
 if(rev92SpeedWatch===null)rev92StartSpeedometer();
 else rev92StopSpeedometer(true);
}

rev92EnsureSpeedometer();
setTimeout(rev92EnsureSpeedometer,120);
setInterval(rev92EnsureSpeedometer,1500);
window.addEventListener("pagehide",()=>rev92StopSpeedometer(true));
'''
if "</body>" not in text:
    raise RuntimeError("Document body is missing")
text = text.replace("</body>", "<script>" + rev92_script + "</script>\n</body>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev92-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="92";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
