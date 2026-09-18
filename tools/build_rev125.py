from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev124.py")
old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.124", "Rev.125")

registration = 'navigator.serviceWorker.register("./sw.js?v=124",{updateViaCache:"none"})'
if text.count(registration) != 1:
    raise RuntimeError("Rev124 service worker registration is missing")
text = text.replace(registration, registration.replace("v=124", "v=125"), 1)

record_css = r'''

/* Rev125: one-touch screen recording control for CCTV viewing. */
.cctv-record-panel{margin:0 0 12px;padding:11px;border:2px solid #df3d3d;border-radius:16px;background:#fff4f4}
.cctv-record-btn{width:100%;min-height:50px;border:0;border-radius:13px;background:#d92f2f;color:#fff;font:950 16px/1.2 inherit;cursor:pointer;box-shadow:0 3px 0 #971e1e}
.cctv-record-btn:active{transform:translateY(1px);box-shadow:0 1px 0 #971e1e}
.cctv-record-btn.recording{background:#15191f;box-shadow:0 3px 0 #000;animation:rev125Pulse 1.15s infinite}
.cctv-record-help{margin-top:7px;color:#5f3333;font-size:11.5px;font-weight:800;line-height:1.42;text-align:center}
.cctv-record-status{display:none;margin-top:8px;padding:8px 9px;border-radius:10px;background:#ffe2e2;color:#8a1616;font-size:12px;font-weight:950;text-align:center}
.cctv-record-status.show{display:block}
@keyframes rev125Pulse{50%{opacity:.72}}
'''
if "</style>" not in text:
    raise RuntimeError("Main style block is missing")
text = text.replace("</style>", record_css + "\n</style>", 1)

traffic_body = '''    <div class="traffic-body">
      <a class="traffic-choice yangjae"'''
record_panel = '''    <div class="traffic-body">
      <div class="cctv-record-panel">
        <button class="cctv-record-btn" id="cctvRecordBtn" type="button">● CCTV 화면녹화 시작</button>
        <div class="cctv-record-help">먼저 녹화를 시작하고 “전체 화면”을 선택한 뒤 CCTV를 여세요. 시청 후 이 화면으로 돌아와 녹화 정지를 누르면 저장됩니다.</div>
        <div class="cctv-record-status" id="cctvRecordStatus" role="status" aria-live="polite"></div>
      </div>
      <a class="traffic-choice yangjae"'''
if text.count(traffic_body) != 1:
    raise RuntimeError("Traffic modal body anchor is missing or duplicated")
text = text.replace(traffic_body, record_panel, 1)

# Keep the timetable app alive while the selected CCTV opens in a separate tab/app.
text = re.sub(
    r'(<a class="traffic-choice [^"]+"[^>]*)(>)',
    lambda match: match.group(1) + (' target="_blank"' if ' target=' not in match.group(1) else '') + match.group(2),
    text,
)

record_script = r'''
<script>
(function(){
  const button=document.getElementById("cctvRecordBtn");
  const status=document.getElementById("cctvRecordStatus");
  if(!button||!status)return;
  let recorder=null,stream=null,chunks=[];
  function message(text){status.textContent=text;status.classList.add("show")}
  function reset(){
    recorder=null;stream=null;chunks=[];
    button.classList.remove("recording");
    button.textContent="● CCTV 화면녹화 시작";
  }
  function extension(type){return type&&type.indexOf("mp4")!==-1?"mp4":"webm"}
  function saveRecording(){
    if(!chunks.length){message("녹화된 화면이 없습니다.");reset();return}
    const type=recorder&&recorder.mimeType?recorder.mimeType:"video/webm";
    const blob=new Blob(chunks,{type:type});
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a");
    const stamp=new Date().toISOString().replace(/[:.]/g,"-");
    a.href=url;a.download="1560_CCTV_"+stamp+"."+extension(type);
    document.body.appendChild(a);a.click();a.remove();
    setTimeout(function(){URL.revokeObjectURL(url)},30000);
    message("녹화를 저장했습니다. 다운로드 폴더를 확인하세요.");
    reset();
  }
  function stopRecording(){
    if(recorder&&recorder.state!=="inactive")recorder.stop();
    if(stream)stream.getTracks().forEach(function(track){track.stop()});
  }
  async function startRecording(){
    if(!navigator.mediaDevices||!navigator.mediaDevices.getDisplayMedia||!window.MediaRecorder){
      message("이 브라우저는 웹 화면녹화를 지원하지 않습니다. 휴대전화 상단 빠른 설정의 ‘화면 녹화’를 사용하세요.");
      return;
    }
    try{
      stream=await navigator.mediaDevices.getDisplayMedia({video:{frameRate:{ideal:30,max:60}},audio:false});
      const types=["video/mp4","video/webm;codecs=vp9","video/webm;codecs=vp8","video/webm"];
      const mime=types.find(function(type){return MediaRecorder.isTypeSupported(type)});
      recorder=mime?new MediaRecorder(stream,{mimeType:mime}):new MediaRecorder(stream);
      chunks=[];
      recorder.ondataavailable=function(event){if(event.data&&event.data.size)chunks.push(event.data)};
      recorder.onstop=saveRecording;
      stream.getVideoTracks()[0].addEventListener("ended",function(){if(recorder&&recorder.state!=="inactive")recorder.stop()});
      recorder.start(1000);
      button.classList.add("recording");
      button.textContent="■ CCTV 화면녹화 정지·저장";
      message("● 녹화 중입니다. 아래에서 CCTV를 여세요.");
    }catch(error){
      reset();
      if(error&&error.name==="NotAllowedError")message("화면공유가 취소되었습니다. 다시 눌러 ‘전체 화면’을 선택하세요.");
      else message("화면녹화를 시작하지 못했습니다. 휴대전화 기본 화면 녹화를 사용하세요.");
    }
  }
  button.addEventListener("click",function(){
    if(recorder&&recorder.state==="recording")stopRecording();
    else startRecording();
  });
  window.addEventListener("pagehide",function(){if(recorder&&recorder.state==="recording")stopRecording()});
})();
</script>
'''
if "</body>" not in text:
    raise RuntimeError("Closing body tag is missing")
text = text.replace("</body>", record_script + "\n</body>", 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev125-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="125";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
