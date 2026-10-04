from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base = Path(__file__).with_name("build_rev140.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old

index = root / "index.html"
html = index.read_text(encoding="utf-8")
registration = 'navigator.serviceWorker.register("./sw.js?v=140",{updateViaCache:"none"})'
if html.count(registration) != 1 or "Rev.140" not in html:
    raise RuntimeError("Expected Rev140 before applying Korean dates")

# Only application constructors change. Date.now(), GPS elapsed times and the
# browser's native Date remain real timestamps. Calendar constructors/setters
# and lunar formatting all use the same Korean civil date.
html, count = re.subn(r"\bnew Date\(", "new TimetableDate(", html)
if count < 20:
    raise RuntimeError("Expected calendar, clock and timetable date constructors")
for before, after in [
    ('{month:"numeric",day:"numeric"}', '{timeZone:"Asia/Seoul",month:"numeric",day:"numeric"}'),
    ('{calendar:"chinese",month:"numeric",day:"numeric"}', '{timeZone:"Asia/Seoul",calendar:"chinese",month:"numeric",day:"numeric"}'),
]:
    if html.count(before) != 1:
        raise RuntimeError("Expected lunar formatter: " + before)
    html = html.replace(before, after, 1)

helper = r'''/* Rev141: app-only Korean civil dates; native Date and timestamps stay intact. */
class TimetableDate extends Date {
  constructor(...args) {
    if (args.length >= 2) super(Date.UTC(...args) - 9 * 60 * 60 * 1000);
    else if (args.length === 1) super(args[0]);
    else super();
  }
  getTimezoneOffset() { return -540; }
}
for (const part of ["FullYear","Month","Date","Day","Hours","Minutes","Seconds","Milliseconds"]) {
  Object.defineProperty(TimetableDate.prototype, "get" + part, {
    value: function() { return new Date(this.getTime() + 32400000)["getUTC" + part](); }
  });
}
for (const part of ["FullYear","Month","Date","Hours","Minutes","Seconds","Milliseconds"]) {
  Object.defineProperty(TimetableDate.prototype, "set" + part, {
    value: function(...args) {
      const civil = new Date(this.getTime() + 32400000);
      return this.setTime(civil["setUTC" + part](...args) - 32400000);
    }
  });
}
'''
html = html.replace("<head>", '<head>\n<script id="rev141-korea-date">\n' + helper + "</script>", 1)
html = html.replace("Rev.140", "Rev.141")
html = html.replace(registration, registration.replace("v=140", "v=141"), 1)
index.write_text(html, encoding="utf-8")

sw = root / "sw.js"
text = sw.read_text(encoding="utf-8")
text = text.replace("1560-timetable-rev140-v1", "1560-timetable-rev141-v1")
text = text.replace('REVISION="140"', 'REVISION="141"')
sw.write_text(text, encoding="utf-8")

redirect = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=./">
<title>1560 최신 시간표로 이동</title>
<script>
const target = new URL("./", location.href);
target.search = location.search;
target.searchParams.delete("v");
target.searchParams.delete("swfix");
target.hash = location.hash;
location.replace(target.href);
</script></head><body><a href="./">최신 1560 시간표 열기</a></body></html>
'''
for revision in (94, 95, 96):
    legacy = root / f"1560_timetable_Rev{revision}_KCC_CCTV.html"
    if not legacy.exists():
        raise RuntimeError("Legacy timetable missing: " + str(legacy))
    legacy.write_text(redirect, encoding="utf-8")
