from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev78.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.78", "Rev.79")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=78",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=79",{updateViaCache:"none"})',
    1,
)

# Rev79: split the combined photo/Gyeonggi Bus control into two touch targets.
# The thumbnail opens the large photo; the text opens the official bus site.
old_button = '''<button type="button" id="rev77-photo-thumb" aria-haspopup="dialog" aria-controls="rev77-photo-modal" aria-label="1560 감사 이미지 크게 보기"><img id="rev77-photo-thumb-img" alt="1560 감사 이미지 미리보기"><span>경기버스</span></button>'''
new_card = '''<div id="rev79-gyeonggi-card" aria-label="경기버스와 1560 감사 이미지">
      <button type="button" id="rev77-photo-thumb" aria-haspopup="dialog" aria-controls="rev77-photo-modal" aria-label="1560 감사 이미지 크게 보기"><img id="rev77-photo-thumb-img" alt="1560 감사 이미지 미리보기"></button>
      <a id="rev79-gyeonggi-link" href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" aria-label="경기버스정보 열기"><span>경기</span><span>버스</span></a>
    </div>'''
if text.count(old_button) != 1:
    raise RuntimeError("Rev78 combined photo button was not found exactly once")
text = text.replace(old_button, new_card, 1)

css = r'''
/* Rev79: photo and Gyeonggi Bus are separate, clearly tappable controls. */
#rev79-gyeonggi-card{
  min-width:0;min-height:64px;display:grid;grid-template-columns:minmax(0,1fr) 52px;
  align-items:stretch;overflow:hidden;border-radius:18px;background:#f7f8fa;
  box-shadow:0 2px 0 #aeb7c1;
}
.info-bar #rev79-gyeonggi-card #rev77-photo-thumb{
  width:100%;min-width:0;min-height:64px;margin:0;padding:6px;border:0;border-radius:0;
  display:flex;align-items:center;justify-content:center;background:transparent;box-shadow:none;
}
#rev79-gyeonggi-card #rev77-photo-thumb img{
  width:72px;height:45px;max-width:100%;object-fit:cover;border-radius:8px;
  box-shadow:0 2px 7px rgba(0,0,0,.24);pointer-events:none;
}
.info-bar #rev79-gyeonggi-link{
  min-width:0;min-height:64px;margin:0;padding:5px 4px;border:0;border-left:1px solid #d8dde3;
  border-radius:0;background:transparent;color:#11151b;box-shadow:none;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  font-size:16px;font-weight:950;line-height:1.04;text-decoration:none;
}
#rev79-gyeonggi-card #rev77-photo-thumb:focus-visible,
#rev79-gyeonggi-link:focus-visible{outline:3px solid #177226;outline-offset:-3px}
#rev79-gyeonggi-card #rev77-photo-thumb:active,
#rev79-gyeonggi-link:active{background:#e7ebef}
@media(max-width:380px){
  #rev79-gyeonggi-card{grid-template-columns:minmax(0,1fr) 44px}
  #rev79-gyeonggi-card #rev77-photo-thumb img{width:56px;height:40px}
  .info-bar #rev79-gyeonggi-link{font-size:14px}
}
'''
text = text.replace("</style>", css + "\n</style>", 1)

old_placer = '''  function placeRev78Photo(){
    const thumb=document.getElementById("rev77-photo-thumb");
    const bar=document.querySelector(".info-bar");
    if(!thumb||!bar)return;
    const old=[...bar.querySelectorAll("a,button")].find(el=>el!==thumb&&(el.textContent||"").includes("경기버스"));
    if(old)old.remove();
    if(thumb.parentElement!==bar)bar.appendChild(thumb);
    thumb.hidden=false;
    thumb.style.display="flex";
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",placeRev78Photo,{once:true});
  else placeRev78Photo();
  setTimeout(placeRev78Photo,300);'''
new_placer = '''  function placeRev79GyeonggiCard(){
    const card=document.getElementById("rev79-gyeonggi-card");
    const bar=document.querySelector(".info-bar");
    if(!card||!bar)return;
    const old=[...bar.children].find(el=>el!==card&&(el.textContent||"").trim()==="경기버스");
    if(old)old.remove();
    if(card.parentElement!==bar)bar.appendChild(card);
    card.hidden=false;
    card.style.display="grid";
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",placeRev79GyeonggiCard,{once:true});
  else placeRev79GyeonggiCard();
  setTimeout(placeRev79GyeonggiCard,300);'''
if old_placer not in text:
    raise RuntimeError("Rev78 photo placement script was not found")
text = text.replace(old_placer, new_placer, 1)
index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev79-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="79";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
