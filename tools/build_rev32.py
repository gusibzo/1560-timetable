from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev31.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.31", "Rev.32")

# Close the GPS/map popup first, force the browser to paint the timetable,
# and only then launch NAVER Map. This prevents the popup remaining visible
# when the user returns from the map app.
old_helper = r'''function rev31OpenExternal(url){
 const link=document.createElement("a");
 link.href=url;
 link.target="_blank";
 link.rel="noopener noreferrer";
 link.style.display="none";
 document.body.appendChild(link);
 link.click();
 setTimeout(()=>link.remove(),600);
}'''
new_helper = r'''function rev32HideGpsPopup(){
 if(typeof gpsModal!=="undefined"&&gpsModal){
  gpsModal.classList.remove("open");
  gpsModal.setAttribute("aria-hidden","true");
 }
 if(typeof gpsQuick!=="undefined"&&gpsQuick)gpsQuick.classList.remove("active");
 if(document.activeElement&&typeof document.activeElement.blur==="function")document.activeElement.blur();
 void document.body.offsetHeight;
}
function rev32OpenExternal(url){
 rev32HideGpsPopup();
 requestAnimationFrame(()=>requestAnimationFrame(()=>{
  setTimeout(()=>{
   const link=document.createElement("a");
   link.href=url;
   link.target="_blank";
   link.rel="noopener noreferrer";
   link.style.display="none";
   document.body.appendChild(link);
   link.click();
   setTimeout(()=>link.remove(),600);
  },180);
 }));
}'''
if old_helper not in text:
    raise RuntimeError("Rev31 external launcher helper was not found")
text = text.replace(old_helper, new_helper, 1)
text = text.replace("rev31OpenExternal(", "rev32OpenExternal(")

old_close = 'if(typeof closeGps==="function")closeGps();'
new_close = 'rev32HideGpsPopup();'
if old_close not in text:
    raise RuntimeError("GPS close line was not found")
text = text.replace(old_close, new_close, 1)

# Also force-close the popup whenever this timetable page becomes active again.
return_marker = 'function rev30ReturnToTimetable(){\n if(typeof gpsModal!=="undefined"&&gpsModal.classList.contains("open")&&typeof closeGps==="function")closeGps();\n}'
return_replacement = 'function rev30ReturnToTimetable(){\n if(typeof rev32HideGpsPopup==="function")rev32HideGpsPopup();\n}'
if return_marker not in text:
    raise RuntimeError("Return-to-timetable handler was not found")
text = text.replace(return_marker, return_replacement, 1)

text = text.replace(
    "※ 네이버지도는 별도 화면으로 열려 1560 시간표가 그대로 남습니다. 지도에서 나오면 시간표로 돌아옵니다.",
    "※ 네이버지도 버튼을 누르는 순간 지도 창이 먼저 닫힙니다. 지도에서 나오면 바로 1560 시간표가 보입니다.",
    1,
)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev32-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
