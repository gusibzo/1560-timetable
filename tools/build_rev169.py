"""Close CCTV in place, revealing the unchanged timetable immediately."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev168.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=168",{updateViaCache:"none"})'
if html.count(registration) != 1:
    raise RuntimeError('Expected Rev168 input')
html, count = re.subn(r'(href="\./cctv\.html\?channel=\d+&amp;v=)(?:162|168)(")', r'\g<1>169\2', html)
if count != 4:
    raise RuntimeError('Expected four direct CCTV entries')
overlay = Path(__file__).with_name('rev169_cctv_overlay.html').read_text(encoding='utf-8')
html = html.replace('</body>', overlay + '\n</body>', 1)
html = html.replace('Rev.168', 'Rev.169').replace(registration, registration.replace('v=168', 'v=169'), 1)
index.write_text(html, encoding='utf-8')

viewer = root / 'cctv.html'
page = viewer.read_text(encoding='utf-8')
before = '      location.replace(timetable);'
after = '''      if (new URL(location.href).searchParams.get('embedded') === '1' && window.parent !== window) {
        window.parent.postMessage({type:'1560-cctv-close'}, location.origin);
        return;
      }
      location.replace(timetable);'''
if page.count(before) != 1:
    raise RuntimeError('Expected standalone close handler')
page = page.replace(before, after, 1)
# The provider header is 90px tall and contains its history-back X. In the
# embedded viewer, clip that header and its bottom navigation out of view.
# The parent dialog owns the visible X, outside both nested frames.
style = '''<script id="rev169-embedded-viewer">
if (new URLSearchParams(location.search).get('embedded') === '1') document.documentElement.classList.add('cctv-embedded');
</script>
<style id="rev169-embedded-style">
.cctv-embedded body{grid-template-rows:minmax(0,1fr) auto}
.cctv-embedded body>header,.cctv-embedded #cctvClose,.cctv-embedded #cctvVideoHeading{display:none}
.cctv-embedded .video-window{isolation:isolate}
.cctv-embedded #cctvFrame{position:absolute;left:0;top:-100px;width:100%;height:calc(100% + 176px)}
</style>
'''
page = page.replace('</head>', style + '</head>', 1)
page = page.replace('실시간 교통 영상 · Rev.168', '실시간 교통 영상 · Rev.169')
page = page.replace("register('./sw.js?v=162'", "register('./sw.js?v=169'")
viewer.write_text(page, encoding='utf-8')

sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev168-v1', '1560-timetable-rev169-v1').replace('REVISION="168"', 'REVISION="169"')
sw.write_text(text, encoding='utf-8')
