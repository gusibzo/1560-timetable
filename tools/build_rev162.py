from pathlib import Path
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev161.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=161",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.161' not in html:
    raise RuntimeError('Expected Rev161 input')
for channel in (6043, 100, 78):
    before = f'href="./cctv.html?channel={channel}"'
    if html.count(before) != 1:
        raise RuntimeError('Expected unique CCTV entry')
    html = html.replace(before, f'href="./cctv.html?channel={channel}&amp;v=162"')
html = html.replace('Rev.161', 'Rev.162').replace(registration, registration.replace('v=161', 'v=162'), 1)
index.write_text(html, encoding='utf-8')

viewer = root / 'cctv.html'
page = viewer.read_text(encoding='utf-8')
anchor = 'aria-label="CCTV 닫고 시간표로 돌아가기">×</a>'
if page.count(anchor) != 1:
    raise RuntimeError('Expected direct timetable close link')
page = page.replace(anchor, 'aria-label="CCTV 닫고 시간표로 돌아가기"><span aria-hidden="true">×</span><small>시간표</small></a><div id="cctvVideoHeading"><strong id="cctvVideoTitle">도로 CCTV</strong><span>실시간 교통 영상 · Rev.162</span></div>', 1)
# Mask the whole provider header, not just a guessed close-button corner.
# Keep video controls and replay prompts below the mask interactive.
style = '''<style id="rev162-cctv-header-style">
#cctvVideoHeading{position:absolute;z-index:1;inset:0 0 auto;height:100px;padding:18px 106px 12px 16px;display:flex;flex-direction:column;justify-content:center;gap:5px;background:#0f0f0f;pointer-events:auto}
#cctvVideoTitle{font-size:20px;line-height:1.3;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#cctvVideoHeading>span{font-size:12px;color:#c7d9e8}
#cctvClose{width:100px;height:100px;display:flex;flex-direction:column;justify-content:center;gap:0;background:#173d60;border-left:1px solid #6286a6;font-size:54px}
#cctvClose small{font-size:16px;line-height:1.3;font-weight:800}
</style>
'''
page = page.replace('</head>', style + '</head>', 1)
if page.count('    frame.src = url.href;') != 1:
    raise RuntimeError('Expected CCTV navigation')
page = page.replace('    frame.src = url.href;', '''    // Camera switching replaces the frame document instead of accumulating
    // camera entries in the browser's joint session history.
    try {
      if (!frame.contentWindow) throw new Error('Frame not ready');
      frame.contentWindow.location.replace(url.href);
    } catch (_) { frame.src = url.href; }''', 1)
anchor = "    title.textContent = camera.road + ' · ' + camera.name;"
page = page.replace(anchor, anchor + "\n    document.getElementById('cctvVideoTitle').textContent = title.textContent;", 1)
# A phone may remain in the CCTV page without ever revisiting index.html.
# Register/update here too so it can receive the same cache recovery as the app.
page = page.replace('</body>', '''<script id="rev162-viewer-update">
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js?v=162', {updateViaCache:'none'})
    .then(registration => registration.update()).catch(() => {});
}
</script>
</body>''', 1)
viewer.write_text(page, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev161-v1', '1560-timetable-rev162-v1').replace('REVISION="161"', 'REVISION="162"')
sw.write_text(text, encoding='utf-8')
