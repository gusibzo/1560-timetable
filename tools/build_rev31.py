from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev30.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.30", "Rev.31")

# Keep the timetable browser tab alive by launching NAVER Map from a separate tab/context.
helper_js = r'''
function rev31OpenExternal(url){
 const link=document.createElement("a");
 link.href=url;
 link.target="_blank";
 link.rel="noopener noreferrer";
 link.style.display="none";
 document.body.appendChild(link);
 link.click();
 setTimeout(()=>link.remove(),600);
}
'''
marker = "const naverMapOpen=document.getElementById(\"naverMapOpen\");"
if marker not in text:
    raise RuntimeError("NAVER Map launcher marker was not found")
text = text.replace(marker, helper_js + "\n" + marker, 1)

android_old = 'location.href=`intent://map?appname=${appName}#Intent;scheme=nmap;action=android.intent.action.VIEW;category=android.intent.category.BROWSABLE;package=com.nhn.android.nmap;end`;'
android_new = 'rev31OpenExternal(`intent://map?appname=${appName}#Intent;scheme=nmap;action=android.intent.action.VIEW;category=android.intent.category.BROWSABLE;package=com.nhn.android.nmap;end`);'
if android_old not in text:
    raise RuntimeError("Android NAVER Map launch line was not found")
text = text.replace(android_old, android_new, 1)

ios_old = 'location.href=`nmap://map?appname=${appName}`;'
ios_new = 'rev31OpenExternal(`nmap://map?appname=${appName}`);'
if ios_old not in text:
    raise RuntimeError("iOS NAVER Map launch line was not found")
text = text.replace(ios_old, ios_new, 1)

store_old = 'location.href="https://apps.apple.com/kr/app/id311867728";'
store_new = 'rev31OpenExternal("https://apps.apple.com/kr/app/id311867728");'
text = text.replace(store_old, store_new, 1)

text = text.replace(
    "※ 네이버지도 앱에서 빠져나오면 지도 창은 자동으로 닫히고 1560 시간표가 바로 보입니다.",
    "※ 네이버지도는 별도 화면으로 열려 1560 시간표가 그대로 남습니다. 지도에서 나오면 시간표로 돌아옵니다.",
    1,
)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev31-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
