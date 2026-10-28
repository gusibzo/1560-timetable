"""Include the same public KMA snapshot in HTML to avoid a startup download."""
import json
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
data=json.loads((root/'weather/kma.json').read_text(encoding='utf-8'))
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
index=root/'index.html'
html=index.read_text(encoding='utf-8')
anchor='<script id="rev171-outdoor-script">'
if html.count(anchor)!=1 or 'id="kmaInitialSnapshot"' in html:
    raise RuntimeError('Expected one weather controller without an embedded snapshot')
html=html.replace(anchor,'<script id="kmaInitialSnapshot" type="application/json">'+payload+'</script>\n'+anchor,1)
index.write_text(html,encoding='utf-8')
