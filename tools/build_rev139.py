from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base = Path(__file__).with_name("build_rev138.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old

index = root / "index.html"
html = index.read_text(encoding="utf-8")
registration = 'navigator.serviceWorker.register("./sw.js?v=138",{updateViaCache:"none"})'
if html.count(registration) != 1:
    raise RuntimeError("Rev138 service-worker registration is missing")
if 'class="time"' not in html or "rev55-route-sign" not in html:
    raise RuntimeError("Timetable bus marker is missing")
css = "\n/* Rev139: approved 3D hydrogen bus for the current timetable marker. */\nbody .grid tbody td.next > .time{\n  position:relative!important;\n  display:inline-block!important;\n  width:70px!important;\n  min-width:70px!important;\n  height:88px!important;\n  min-height:88px!important;\n  padding:73px 0 0!important;\n  left:-7px!important;\n  border:0!important;\n  border-radius:9px!important;\n  background:transparent url(\"./icons/icon-192.png\") center top / 70px 70px no-repeat!important;\n  color:#111827!important;\n  font-size:14px!important;\n  line-height:15px!important;\n  font-weight:950!important;\n  letter-spacing:-.3px!important;\n  text-shadow:0 1px 0 rgba(255,255,255,.7)!important;\n  box-shadow:none!important;\n  animation:rev139BusPulse 1.08s ease-in-out infinite alternate!important;\n}\nbody .grid tbody td.next > .time::before,\nbody .grid tbody td.next > .time::after{\n  content:none!important;\n  display:none!important;\n}\nbody .grid tbody td.next > .time > .rev55-route-sign{\n  top:13px!important;\n  left:18px!important;\n  right:18px!important;\n  height:7px!important;\n  border:0!important;\n  border-radius:1px!important;\n  font-size:5.8px!important;\n  letter-spacing:.2px!important;\n  gap:1px!important;\n  background:#11161b!important;\n}\nbody[data-day=\"sunday\"] .grid tbody td.next.edge > .time{\n  color:#fff!important;\n  text-shadow:0 1px 2px rgba(0,0,0,.8)!important;\n}\n@keyframes rev139BusPulse{\n  from{filter:drop-shadow(0 0 3px rgba(190,235,50,.45));transform:translateY(0) scale(.99)}\n  to{filter:drop-shadow(0 0 8px rgba(190,235,50,.8));transform:translateY(-1px) scale(1.025)}\n}\n@media(max-width:380px){\n  body .grid tbody td.next > .time{\n    width:66px!important;min-width:66px!important;\n    height:83px!important;min-height:83px!important;\n    padding-top:69px!important;\n    background-size:66px 66px!important;\n    left:-6px!important;font-size:13.5px!important;line-height:14px!important;\n  }\n  body .grid tbody td.next > .time > .rev55-route-sign{\n    top:12px!important;left:17px!important;right:17px!important;\n    height:7px!important;font-size:5.5px!important;\n  }\n}\n@media(prefers-reduced-motion:reduce){\n  body .grid tbody td.next > .time{animation:none!important}\n}\n"
if html.count("</style>") < 1:
    raise RuntimeError("Main style block is missing")
html = html.replace("</style>", "\n" + css + "\n</style>", 1)
html = html.replace("Rev.137", "Rev.139")
html = html.replace(registration, registration.replace("v=138", "v=139"), 1)
index.write_text(html, encoding="utf-8")

sw = root / "sw.js"
text = sw.read_text(encoding="utf-8")
text = text.replace('const CACHE_NAME="1560-timetable-rev138-v1";', 'const CACHE_NAME="1560-timetable-rev139-v1";')
text = text.replace('const REVISION="138";', 'const REVISION="139";')
sw.write_text(text, encoding="utf-8")
