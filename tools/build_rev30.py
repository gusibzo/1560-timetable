from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev29.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.29", "Rev.30")

# Close the map/speedometer popup before launching NAVER Map, so returning shows the timetable.
old_click = '''if(naverMapOpen){
 naverMapOpen.addEventListener("click",e=>{
  e.preventDefault();
  const appName=encodeURIComponent(location.origin+location.pathname);'''
new_click = '''if(naverMapOpen){
 naverMapOpen.addEventListener("click",e=>{
  e.preventDefault();
  if(typeof closeGps==="function")closeGps();
  const appName=encodeURIComponent(location.origin+location.pathname);'''
if old_click not in text:
    raise RuntimeError("NAVER Map launcher block was not found")
text = text.replace(old_click, new_click, 1)

return_js = r'''
/* Rev30: whenever the browser becomes active again after a map app, show the timetable. */
function rev30ReturnToTimetable(){
 if(typeof gpsModal!=="undefined"&&gpsModal.classList.contains("open")&&typeof closeGps==="function")closeGps();
}
window.addEventListener("pageshow",rev30ReturnToTimetable);
window.addEventListener("focus",rev30ReturnToTimetable);
document.addEventListener("visibilitychange",()=>{if(!document.hidden)rev30ReturnToTimetable()});
'''
marker = "const DATA={"
if marker not in text:
    raise RuntimeError("script insertion point was not found")
text = text.replace(marker, return_js + "\n" + marker, 1)

text = text.replace(
    "※ 네이버지도 버튼은 지도 앱을 바로 엽니다. 뒤로가기를 누르면 1560 시간표로 돌아옵니다.",
    "※ 네이버지도 앱에서 빠져나오면 지도 창은 자동으로 닫히고 1560 시간표가 바로 보입니다.",
    1,
)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev30-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
