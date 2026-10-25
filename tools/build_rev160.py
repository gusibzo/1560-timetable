from pathlib import Path
import json
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev159.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

index = root / 'index.html'
html = index.read_text(encoding='utf-8')
registration = 'navigator.serviceWorker.register("./sw.js?v=159",{updateViaCache:"none"})'
if html.count(registration) != 1 or 'Rev.159' not in html:
    raise RuntimeError('Expected Rev159 input')

# Only the three direct Naver CCTV entries use our camera navigation page.
pattern = r'(<a class="traffic-choice [^"]+"[^>]*href=")https://rtt\.map\.naver\.com/end-traffic/bridges/cctv/web/home\?([^\"]+)(")'
def local_viewer(match):
    query = match[2].replace('&amp;', '&')
    channel = re.search(r'(?:^|&)channel=(\d+)(?:&|$)', query)
    if not channel:
        raise RuntimeError('Missing CCTV channel')
    return match[1] + './cctv.html?channel=' + channel[1] + match[3]
html, count = re.subn(pattern, local_viewer, html)
if count != 3:
    raise RuntimeError('Expected Banpo, Yangjae and Seoul toll CCTV links')

template = Path(__file__).with_name('rev160_cctv.html').read_text(encoding='utf-8')
cameras = json.loads(Path(__file__).with_name('rev160_cctv_cameras.json').read_text(encoding='utf-8'))
if len({camera['channel'] for camera in cameras}) != len(cameras):
    raise RuntimeError('Duplicate CCTV channels')
if not {6043, 100, 78}.issubset({camera['channel'] for camera in cameras}):
    raise RuntimeError('Missing entry camera')
data = json.dumps(cameras, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
if template.count('__CAMERA_DATA__') != 1:
    raise RuntimeError('Missing CCTV data placeholder')
(root / 'cctv.html').write_text(template.replace('__CAMERA_DATA__', data), encoding='utf-8')
html = html.replace('Rev.159', 'Rev.160').replace(registration, registration.replace('v=159', 'v=160'), 1)
index.write_text(html, encoding='utf-8')
sw = root / 'sw.js'
text = sw.read_text(encoding='utf-8').replace('1560-timetable-rev159-v1', '1560-timetable-rev160-v1').replace('REVISION="159"', 'REVISION="160"')
text, count = re.subn(r'const CORE=\[', 'const CORE=["./cctv.html",', text)
if count != 1:
    raise RuntimeError('Expected service worker core cache')
anchor = '  event.respondWith((async()=>{'
if text.count(anchor) != 1:
    raise RuntimeError('Expected main service worker fetch handler')
viewer_cache = '''  // Keep the CCTV page separate from the timetable navigation cache.
  const viewerKey=new URL("./cctv.html",self.registration.scope);
  if(request.mode==="navigate"&&url.pathname===viewerKey.pathname){
    event.respondWith((async()=>{
      const cache=await caches.open(CACHE_NAME);
      try{
        const fresh=await fetch(request,{cache:"no-store"});
        if(fresh&&fresh.ok)await cache.put(viewerKey,fresh.clone());
        return fresh;
      }catch(_){return (await cache.match(viewerKey))||Response.error();}
    })());
    return;
  }

'''
text = text.replace(anchor, viewer_cache + anchor, 1)
sw.write_text(text, encoding='utf-8')
