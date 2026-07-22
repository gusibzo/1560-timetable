from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev28.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.28", "Rev.29")

# Open the installed NAVER Map app directly instead of showing its mobile-web app banner.
old_link = '<a class="naver" href="https://m.map.naver.com/" target="_blank" rel="noopener noreferrer">🗺️ 네이버지도</a>'
new_link = '<a class="naver" id="naverMapOpen" href="nmap://map?appname=https%3A%2F%2Fgusibzo.github.io%2F1560-timetable%2F">🗺️ 네이버지도</a>'
if old_link not in text:
    raise RuntimeError("NAVER Map link insertion point was not found")
text = text.replace(old_link, new_link, 1)

launcher_js = r'''
const naverMapOpen=document.getElementById("naverMapOpen");
if(naverMapOpen){
 naverMapOpen.addEventListener("click",e=>{
  e.preventDefault();
  const appName=encodeURIComponent(location.origin+location.pathname);
  const ua=navigator.userAgent||"";
  if(/Android/i.test(ua)){
   location.href=`intent://map?appname=${appName}#Intent;scheme=nmap;action=android.intent.action.VIEW;category=android.intent.category.BROWSABLE;package=com.nhn.android.nmap;end`;
   return;
  }
  if(/iPhone|iPad|iPod/i.test(ua)){
   const clickedAt=Date.now();
   location.href=`nmap://map?appname=${appName}`;
   setTimeout(()=>{
    if(Date.now()-clickedAt<2200&&!document.hidden){
     location.href="https://apps.apple.com/kr/app/id311867728";
    }
   },1600);
   return;
  }
  window.open("https://map.naver.com/","_blank","noopener,noreferrer");
 });
}
'''
marker = "const DATA={"
if marker not in text:
    raise RuntimeError("script insertion point was not found")
text = text.replace(marker, launcher_js + "\n" + marker, 1)

text = text.replace(
    "※ 지도를 본 뒤 휴대폰의 뒤로가기를 누르면 1560 시간표로 돌아옵니다.",
    "※ 네이버지도 버튼은 지도 앱을 바로 엽니다. 뒤로가기를 누르면 1560 시간표로 돌아옵니다.",
    1,
)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev29-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
