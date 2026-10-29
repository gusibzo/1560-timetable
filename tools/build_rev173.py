"""Recover weather failures and keep the CCTV viewer on the same app revision."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv)>1 else '_site')
base = Path(__file__).with_name('build_rev172.py')
old = sys.argv[:]
try:
    sys.argv = [str(base),str(root)]
    runpy.run_path(str(base),run_name='__main__')
finally:
    sys.argv = old
index = root/'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=172",{updateViaCache:"none"})'
if html.count(registration)!=1:
    raise RuntimeError('Expected Rev172 input')
js = Path(__file__).with_name('rev173_outdoor.js').read_text(encoding='utf-8')
html,count = re.subn(r'<script id="rev172-outdoor-script">[\s\S]*?</script>',lambda _: '<script id="rev173-outdoor-script">\n'+js+'\n</script>',html)
if count!=1:
    raise RuntimeError('Expected weather controller')
help_dialog = '''<dialog id="weatherProblem" aria-labelledby="weatherProblemTitle" style="max-width:min(90vw,400px);border:2px solid #60bfff;border-radius:18px;padding:22px;color:#123553;background:#e8f6ff;font:17px/1.6 system-ui">
<h2 id="weatherProblemTitle" style="margin:0;font-size:22px">온도 확인</h2><p id="weatherProblemText"></p>
<div style="display:flex;gap:10px"><button id="weatherTryAgain" type="button" style="font:inherit;font-weight:800;padding:10px 14px;border:0;border-radius:10px;background:#1766bb;color:white">다시 확인</button><button id="weatherProblemClose" type="button" style="font:inherit;padding:10px 14px;border:1px solid #8caac3;border-radius:10px;background:white">닫기</button></div>
</dialog>'''
html=html.replace('<script id="rev173-outdoor-script">',help_dialog+'\n<script id="rev173-outdoor-script">',1)
html=html.replace('Rev.172','Rev.173').replace(registration,registration.replace('v=172','v=173'),1)
html=html.replace('channel=6043&amp;v=169','channel=6043&amp;v=173').replace('channel=100&amp;v=169','channel=100&amp;v=173').replace('channel=78&amp;v=169','channel=78&amp;v=173').replace('channel=6929&amp;v=169','channel=6929&amp;v=173')
html=html.replace("url.searchParams.set('v', '169');", "url.searchParams.set('v', '173');")
# Navigation/loading status belongs to the visible wrapper, not the provider.
index.write_text(html,encoding='utf-8')
viewer=root/'cctv.html'
page=viewer.read_text(encoding='utf-8')
page=page.replace("if ('serviceWorker' in navigator) {", "if ('serviceWorker' in navigator && new URLSearchParams(location.search).get('embedded') !== '1') {")
page=page.replace("register('./sw.js?v=169'", "register('./sw.js?v=173'")
page=page.replace('Rev.169','Rev.173')
page=page.replace('<iframe id="cctvFrame"', '<p id="cctvLoading" role="status" aria-live="polite" style="position:absolute;z-index:2;top:0;left:0;right:0;margin:0;padding:10px;background:#123553;color:#fff;font-size:14px">영상을 불러오고 있습니다…</p><iframe id="cctvFrame"')
page=page.replace("  const status = document.getElementById('cameraStatus');", """  const status = document.getElementById('cameraStatus');
  const loading = document.getElementById('cctvLoading');
  let loadingTimer;
  frame.addEventListener('load', () => {
    clearTimeout(loadingTimer);
    loading.hidden = true;
    status.textContent = title.textContent + ' · 영상 창 연결됨';
  });""")
page=page.replace("    const camera = cameras[index];", """    const camera = cameras[index];
    clearTimeout(loadingTimer);
    loading.hidden = false;
    loading.textContent = '영상을 불러오고 있습니다…';
    loadingTimer = setTimeout(() => {
      loading.textContent = '영상 연결이 늦습니다. 아래 영상 새로고침을 누르거나 네이버에서 열어 주세요.';
    }, 12000);""")
viewer.write_text(page,encoding='utf-8')
sw=root/'sw.js'
text=sw.read_text(encoding='utf-8').replace('1560-timetable-rev172-v1','1560-timetable-rev173-v1').replace('REVISION="172"','REVISION="173"')
start=text.index('    // Recover phones that are still displaying an old cached revision.')
end=text.index('\n  })());',start)
# Network-first already supplies the latest page. Do not interrupt an active
# camera/interaction by force-navigating every window and embedded frame.
text=text[:start]+'    // Fresh pages arrive network-first. Activation must not reload active views.\n'+text[end:]
sw.write_text(text,encoding='utf-8')
