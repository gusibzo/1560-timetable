from pathlib import Path
import re
import shutil
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
source = root / "1560_timetable_Rev95_KCC_CCTV.html"
index = root / "index.html"

if not source.exists():
    raise RuntimeError("Rev95 source file is missing")

shutil.copyfile(source, index)

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev95-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="95";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
