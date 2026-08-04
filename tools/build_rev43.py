from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev42.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.42", "Rev.43")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=42",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=43",{updateViaCache:"none"})',
    1,
)

# Add a clean, compact recreation of the photographed 1560 operation guide above
# the existing interval table. Keep the older table below it for reference.
official_guide = r'''
<section class="official-gap-guide" aria-label="1560 버스시간표 주간 평일 운행 안내">
  <div class="official-gap-heading">
    <h2>1560 버스시간표 <span>(주간·평일)</span></h2>
    <div class="official-kd" aria-label="KD 운송그룹"><b>KD</b> 운송그룹</div>
  </div>
  <div class="official-route-pair">
    <div class="official-route">
      <div class="official-route-name"><strong>1560A</strong> 반포 <span>▶</span> 양재</div>
      <div class="official-route-meta"><span>신논현역</span><b>1시간 10분</b></div>
    </div>
    <div class="official-route">
      <div class="official-route-name"><strong>1560B</strong> 양재 <span>▶</span> 반포</div>
      <div class="official-route-meta"><span>매헌시민의숲</span><b>1시간 5분</b></div>
    </div>
  </div>
  <div class="official-trip-row">
    <div class="official-trip"><strong>1회</strong><span>2시간 35분</span></div>
    <div class="official-trip"><strong>2회</strong><span>2시간 25분</span></div>
    <div class="official-trip"><strong>3회</strong><span>2시간 35분</span></div>
    <div class="official-trip"><strong>4회</strong><span>2시간 35분</span></div>
    <div class="official-trip"><strong>5회</strong><span>2시간 25분</span></div>
  </div>
</section>
'''

old_guide_open = '<section class="route-gap-guide" aria-label="신논현역 평일 주말 공휴일 운행 간격 안내">'
if old_guide_open not in text:
    raise RuntimeError("existing route interval guide was not found")
text = text.replace(
    old_guide_open,
    official_guide.strip() + "\n" + old_guide_open + '\n  <div class="route-gap-title">1560 버스시간표</div>',
    1,
)

# Correct the old table's shortened typo while keeping its established layout.
text = text.replace("2시25분", "2시간25분")

css = r'''
/* Rev43: compact clean operation guide above the existing interval table. */
.official-gap-guide{
  margin-top:15px;
  border:1.5px solid #15191e;
  border-radius:11px;
  overflow:hidden;
  background:#fff;
  color:#111;
  box-shadow:0 1px 0 var(--line),0 8px 24px rgba(0,0,0,.14);
}
.official-gap-heading{
  position:relative;
  min-height:36px;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:5px 92px 5px 10px;
  background:#fff;
  border-bottom:1px solid #111;
}
.official-gap-heading h2{
  margin:0;
  font-size:18px;
  line-height:1.1;
  font-weight:950;
  letter-spacing:-.5px;
  white-space:nowrap;
}
.official-gap-heading h2 span{font-size:.86em}
.official-kd{
  position:absolute;
  right:9px;
  top:50%;
  transform:translateY(-50%);
  color:#1253a0;
  font-size:9.5px;
  font-weight:950;
  white-space:nowrap;
  letter-spacing:-.3px;
}
.official-kd b{
  color:#1761b5;
  font-size:13px;
  font-style:italic;
  margin-right:2px;
  text-shadow:-1px 0 #e53b35;
}
.official-route-pair{
  display:grid;
  grid-template-columns:1fr 1fr;
  background:#e8f4df;
  border-bottom:1px solid #111;
}
.official-route{
  min-width:0;
  padding:5px 7px 4px;
  border-right:1px solid #111;
}
.official-route:last-child{border-right:0}
.official-route-name{
  text-align:center;
  font-size:15px;
  line-height:1.12;
  font-weight:900;
  white-space:nowrap;
  letter-spacing:-.35px;
}
.official-route-name strong{font-size:17px}
.official-route-name span{font-size:11px}
.official-route-meta{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  align-items:center;
  gap:5px;
  margin-top:3px;
  font-size:11.5px;
  line-height:1.1;
  letter-spacing:-.25px;
}
.official-route-meta span{min-width:0;white-space:nowrap}
.official-route-meta b{white-space:nowrap;font-size:11.5px}
.official-trip-row{
  display:grid;
  grid-template-columns:repeat(5,1fr);
  background:#fff;
}
.official-trip{
  min-width:0;
  min-height:49px;
  padding:5px 1px 4px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:3px;
  border-right:1px solid #111;
  text-align:center;
  white-space:nowrap;
}
.official-trip:last-child{border-right:0}
.official-trip strong{font-size:17px;line-height:1;font-weight:950}
.official-trip span{font-size:11.5px;line-height:1.08;font-weight:850;letter-spacing:-.35px}
.route-gap-title{
  min-height:34px;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:4px 8px;
  background:#fff;
  color:#111;
  border-bottom:1px solid #111;
  font-size:17px;
  line-height:1.1;
  font-weight:950;
  letter-spacing:-.4px;
}
@media(max-width:380px){
  .official-gap-heading{min-height:33px;padding-right:77px}
  .official-gap-heading h2{font-size:15.5px}
  .official-kd{right:6px;font-size:8.5px}
  .official-kd b{font-size:11px}
  .official-route{padding:5px 4px 4px}
  .official-route-name{font-size:12.5px}
  .official-route-name strong{font-size:14px}
  .official-route-meta{font-size:9.5px;gap:3px}
  .official-route-meta b{font-size:9.5px}
  .official-trip{min-height:44px;padding:4px 0 3px;gap:2px}
  .official-trip strong{font-size:14px}
  .official-trip span{font-size:9.5px}
  .route-gap-title{min-height:31px;font-size:15px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev43-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="43";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
