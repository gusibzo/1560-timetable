from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base = Path(__file__).with_name("build_rev139.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old

index = root / "index.html"
html = index.read_text(encoding="utf-8")
registration = 'navigator.serviceWorker.register("./sw.js?v=139",{updateViaCache:"none"})'
if html.count(registration) != 1 or "Rev.139" not in html:
    raise RuntimeError("Expected Rev139 site before applying marker layout")

css = r'''
/* Rev140: rounded 3D bus with the live timetable text inside its body. */
body .grid tbody td.next > .time{
  box-sizing:border-box!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:70px!important;
  min-width:70px!important;
  height:70px!important;
  min-height:70px!important;
  padding:34px 0 0!important;
  border-radius:16px!important;
  overflow:hidden!important;
  background:transparent url("./icons/icon-192.png") center / 70px 70px no-repeat!important;
  color:#fff!important;
  font-size:19px!important;
  line-height:24px!important;
  letter-spacing:-.7px!important;
  white-space:nowrap!important;
  text-shadow:0 1px 2px #000,0 0 4px #000,0 0 7px #000!important;
  box-shadow:0 0 0 2px #ffe96a!important;
}
@media(max-width:380px){
  body .grid tbody td.next > .time{
    width:66px!important;
    min-width:66px!important;
    height:66px!important;
    min-height:66px!important;
    padding-top:32px!important;
    border-radius:15px!important;
    background-size:66px 66px!important;
    font-size:18px!important;
    line-height:23px!important;
  }
}
'''
html = html.replace("</style>", css + "\n</style>", 1)
html = html.replace("Rev.139", "Rev.140")
html = html.replace(registration, registration.replace("v=139", "v=140"), 1)
index.write_text(html, encoding="utf-8")

sw = root / "sw.js"
text = sw.read_text(encoding="utf-8")
text = text.replace("1560-timetable-rev139-v1", "1560-timetable-rev140-v1")
text = text.replace('REVISION="139"', 'REVISION="140"')
sw.write_text(text, encoding="utf-8")
