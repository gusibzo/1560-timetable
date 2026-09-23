from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev128.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.128", "Rev.129")

registration = 'navigator.serviceWorker.register("./sw.js?v=128",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev128 service worker registration is missing")
text = text.replace(registration, registration.replace("v=128", "v=129"), 1)

text, removed_css = re.subn(
    r'\n/\* Rev126: Samsung phone screen-recording instructions\. \*/.*?\.cctv-phone-record-note\{[^\n]*\}\n',
    "\n",
    text,
    count=1,
    flags=re.S,
)
if removed_css != 1:
    raise RuntimeError("Screen recording instruction styles are missing")

text, removed_panel = re.subn(
    r'\n      <div class="cctv-phone-record-guide" aria-label="휴대전화 화면 녹화 방법">.*?\n      </div>(?=\n      <a class="traffic-choice yangjae")',
    "",
    text,
    count=1,
    flags=re.S,
)
if removed_panel != 1:
    raise RuntimeError("Screen recording instruction panel is missing")

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev129-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="129";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
