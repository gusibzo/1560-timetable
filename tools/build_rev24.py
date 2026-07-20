from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev23.py")

# Build the established Rev23 site first, then apply only the new Rev24 changes.
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.23", "Rev.24")

# The two TMAP buttons now perform different actions.
text = text.replace(
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/route.jsp" rel="noopener noreferrer">🧭 T맵</a>',
    '<a class="tmap" href="https://www.tmap.co.kr/tmap2/mobile/tmap.jsp?scheme=tmap" rel="noopener noreferrer">🧭 T맵</a>',
)

new_guide = r'''
<section class="route-gap-guide" aria-label="신논현역 평일 주말 공휴일 운행 간격 안내">
  <div class="route-gap-grid rev24-gap-grid">
    <div class="gap-corner" aria-hidden="true"></div>
    <div class="black">1번차(오전)</div>
    <div class="black">2번차(오전)</div>
    <div class="black">나머지차</div>
    <div class="black">막탕(오/전후)</div>

    <div class="gap-station">신논현역</div>
    <div class="black">6:05 AM'</div>
    <div class="black">6:20 AM'</div>
    <div class="black"></div>
    <div class="black"></div>

    <div class="gap-weekday-label">주간(평일)</div>
    <div class="gap-weekday">2시간30분</div>
    <div class="gap-weekday">2시간30분</div>
    <div class="gap-weekday">2시간35분</div>
    <div class="gap-weekday">2시간25분</div>

    <div class="gap-weekend-label">주말.공휴일</div>
    <div class="gap-weekend">2시간25분</div>
    <div class="gap-weekend">2시25분</div>
    <div class="gap-weekend">2시간25분</div>
    <div class="gap-weekend">2시간25분</div>
  </div>
</section>
'''
text, replaced = re.subn(
    r'<section class="route-gap-guide".*?</section>',
    new_guide.strip(),
    text,
    count=1,
    flags=re.S,
)
if replaced != 1:
    raise RuntimeError("route interval guide was not found")

css = r'''
/* Rev24: four-row Shin-nonhyeon interval table */
.rev24-gap-grid{grid-template-columns:1.12fr repeat(4,1fr)}
.rev24-gap-grid>div{border-right:1px solid #111;border-bottom:1px solid #111;min-height:40px}
.rev24-gap-grid>div:nth-child(5n){border-right:0}
.rev24-gap-grid>div:nth-last-child(-n+5){border-bottom:0}
.rev24-gap-grid .gap-corner{position:relative;background:#fff3cf}
.rev24-gap-grid .gap-corner::after{content:"";position:absolute;inset:0;background:linear-gradient(to top right,transparent 49.1%,#111 49.6%,#111 50.4%,transparent 50.9%)}
.rev24-gap-grid .gap-station{background:#c9e8b6;color:#008bd5;font-size:13px;font-weight:950}
.rev24-gap-grid .gap-weekday-label{background:#d4e0f0;color:#111;font-size:13px;font-weight:950;white-space:nowrap}
.rev24-gap-grid .gap-weekday{background:#dce5f3;color:#111;font-size:13px;font-weight:950;white-space:nowrap}
.rev24-gap-grid .gap-weekend-label,.rev24-gap-grid .gap-weekend{background:#fff88e;color:#ff1717;font-size:13px;font-weight:950;white-space:nowrap}
@media(max-width:380px){
 .rev24-gap-grid .black{font-size:10.5px}
 .rev24-gap-grid .gap-station,.rev24-gap-grid .gap-weekday-label,.rev24-gap-grid .gap-weekday,.rev24-gap-grid .gap-weekend-label,.rev24-gap-grid .gap-weekend{font-size:10.5px}
 .rev24-gap-grid>div{padding:7px 1px;min-height:37px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if sw.exists():
    sw_text = sw.read_text(encoding="utf-8")
    sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev24-v1";', sw_text)
    sw.write_text(sw_text, encoding="utf-8")
