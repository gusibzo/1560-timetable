from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev125.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.125", "Rev.126")

registration = 'navigator.serviceWorker.register("./sw.js?v=125",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev125 service worker registration is missing")
text = text.replace(registration, registration.replace("v=125", "v=126"), 1)

# Rev125's browser recorder does not work in Samsung's mobile browser.
text, css_count = re.subn(
    r"\n/\* Rev125: one-touch screen recording control for CCTV viewing\. \*/.*?@keyframes rev125Pulse\{50%\{opacity:\.72\}\}\n",
    "\n",
    text,
    count=1,
    flags=re.S,
)
if css_count != 1:
    raise RuntimeError("Rev125 recorder style block is missing")

old_panel = '''      <div class="cctv-record-panel">
        <button class="cctv-record-btn" id="cctvRecordBtn" type="button">● CCTV 화면녹화 시작</button>
        <div class="cctv-record-help">먼저 녹화를 시작하고 “전체 화면”을 선택한 뒤 CCTV를 여세요. 시청 후 이 화면으로 돌아와 녹화 정지를 누르면 저장됩니다.</div>
        <div class="cctv-record-status" id="cctvRecordStatus" role="status" aria-live="polite"></div>
      </div>'''
new_panel = '''      <div class="cctv-phone-record-guide" aria-label="휴대전화 화면 녹화 방법">
        <div class="cctv-phone-record-title">📱 CCTV 화면 녹화 방법</div>
        <div class="cctv-phone-record-steps">
          <span><b>1</b>CCTV 열기</span>
          <span><b>2</b>화면 위에서 두 번 내리기</span>
          <span><b>3</b>‘화면 녹화’ 누르기</span>
        </div>
        <div class="cctv-phone-record-note">녹화가 끝나면 상단의 정지 ■를 누르세요. 영상은 갤러리에 저장됩니다.</div>
      </div>'''
if text.count(old_panel) != 1:
    raise RuntimeError("Rev125 recorder panel is missing")
text = text.replace(old_panel, new_panel, 1)

text, script_count = re.subn(
    r'\n<script>\n\(function\(\)\{\n  const button=document\.getElementById\("cctvRecordBtn"\);.*?\n\}\)\(\);\n</script>\n',
    "\n",
    text,
    count=1,
    flags=re.S,
)
if script_count != 1:
    raise RuntimeError("Rev125 recorder script is missing")

guide_css = r'''

/* Rev126: Samsung phone screen-recording instructions. */
.cctv-phone-record-guide{margin:0 0 12px;padding:13px 12px;border:2px solid #3978ac;border-radius:16px;background:linear-gradient(135deg,#f3f9ff,#e5f3ff);color:#173c5a;text-align:center}
.cctv-phone-record-title{font-size:17px;font-weight:950;margin-bottom:10px}
.cctv-phone-record-steps{display:grid;gap:7px;text-align:left}
.cctv-phone-record-steps span{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:11px;background:#fff;font-size:13px;font-weight:900;box-shadow:0 1px 3px #2b608322}
.cctv-phone-record-steps b{display:inline-grid;place-items:center;flex:0 0 25px;height:25px;border-radius:50%;background:#2874ad;color:#fff;font-size:14px}
.cctv-phone-record-note{margin-top:9px;font-size:11.5px;font-weight:800;line-height:1.45;color:#43596a}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", guide_css + "\n</style>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev126-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="126";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
