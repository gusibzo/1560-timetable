"""Publish the compact trip alert controls and Monday-first work calendar."""
from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = Path(__file__).with_name('build_rev202.py')
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name='__main__')
finally:
    sys.argv = old

for name in ['index.html', 'cctv.html', 'alarm.html', 'timer-records.html']:
    page = root / name
    html = page.read_text(encoding='utf-8').replace('Rev.202', 'Rev.203').replace('sw.js?v=202', 'sw.js?v=203')
    html = re.sub(r'(channel=\d+&amp;v=)202', r'\g<1>203', html)
    html = html.replace("url.searchParams.set('v', '202');", "url.searchParams.set('v', '203');")
    if name == 'index.html':
        old_week = '<span>일</span><span>월</span><span>화</span><span>수</span><span>목</span><span>금</span><span>토</span>'
        new_week = '<span>월</span><span>화</span><span>수</span><span>목</span><span>금</span><span class="sat">토</span><span class="sun">일</span>'
        old_dates = ',cellCount=Math.ceil((first.getDay()+daysInMonth)/7)*7,start=new TimetableDate(y,m,1-first.getDay())'
        new_dates = ',leading=(first.getDay()+6)%7,cellCount=Math.ceil((leading+daysInMonth)/7)*7,start=new TimetableDate(y,m,1-leading)'
        for old, new in ((old_week, new_week), (old_dates, new_dates)):
            if html.count(old) != 1:
                raise RuntimeError('Expected one work calendar layout')
            html = html.replace(old, new, 1)
        html = html.replace('.calendar-week span:first-child', '.calendar-week .sun')
        html = html.replace('.calendar-week span:last-child', '.calendar-week .sat')
    page.write_text(html, encoding='utf-8')

sw = root / 'sw.js'
code = sw.read_text(encoding='utf-8').replace('1560-timetable-rev202-v1', '1560-timetable-rev203-v1')
sw.write_text(code.replace('REVISION="202"', 'REVISION="203"'), encoding='utf-8')
