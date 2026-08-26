from pathlib import Path
import re
import runpy
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base_builder = Path(__file__).with_name("build_rev83.py")

old_argv = sys.argv[:]
try:
    sys.argv = [str(base_builder), str(root)]
    runpy.run_path(str(base_builder), run_name="__main__")
finally:
    sys.argv = old_argv

index = root / "index.html"
text = index.read_text(encoding="utf-8")
text = text.replace("Rev.83", "Rev.84")
text = text.replace(
    'navigator.serviceWorker.register("./sw.js?v=83",{updateViaCache:"none"})',
    'navigator.serviceWorker.register("./sw.js?v=84",{updateViaCache:"none"})',
    1,
)

# Rev84: when a bus row is selected, calculate current/next departures from
# that bus only. The center counter counts down to the selected bus's next
# departure instead of counting elapsed time since the previous departure.
old_events = '''  const events=rev57TodayEvents(day);
  const now=new Date();'''
new_events = '''  const selectedBusNo=typeof rev63SelectedBus==="function"?Number(rev63SelectedBus()):0;
  const selectedRow=Number.isInteger(selectedBusNo)&&selectedBusNo>=1?data.rows[selectedBusNo-1]:null;
  const events=selectedRow?(()=>{
    const selected=[];
    selectedRow.t.forEach((time,ci)=>{
      if(time)selected.push({time,min:toMin(time),ri:selectedBusNo-1,ci,kind:"base"});
    });
    if(selectedRow.ext)selected.push({time:selectedRow.ext,min:toMin(selectedRow.ext),ri:selectedBusNo-1,ci:4,kind:"ext"});
    return selected.sort((a,b)=>a.min-b.min);
  })():rev57TodayEvents(day);
  const now=new Date();'''
if text.count(old_events) != 1:
    raise RuntimeError("Rev83 briefing event source was not found exactly once")
text = text.replace(old_events, new_events, 1)

old_badge = '  if(dayEl)dayEl.textContent=`${data.label} · ${data.count}대`;'
new_badge = '  if(dayEl)dayEl.textContent=selectedRow?`${selectedBusNo}번 · ${data.label}`:`${data.label} · ${data.count}대`;'
if text.count(old_badge) != 1:
    raise RuntimeError("Rev83 briefing badge was not found exactly once")
text = text.replace(old_badge, new_badge, 1)

old_counter = '''  if(currentEl){
    if(current){
      const elapsed=Math.max(0,Math.floor((nowMin-current.min)*60));
      const hh=String(Math.floor(elapsed/3600)).padStart(2,"0");
      const mm=String(Math.floor((elapsed%3600)/60)).padStart(2,"0");
      const ss=String(elapsed%60).padStart(2,"0");
      currentEl.textContent=current.time;
      if(counterEl)counterEl.textContent=`${hh}:${mm}:${ss}`;
    }else{
      currentEl.textContent="운행 전";
      if(counterEl)counterEl.textContent="00:00:00";
    }
  }'''
new_counter = '''  const countdown=next?Math.max(0,Math.ceil((next.min-nowMin)*60)):0;
  const hh=String(Math.floor(countdown/3600)).padStart(2,"0");
  const mm=String(Math.floor((countdown%3600)/60)).padStart(2,"0");
  const ss=String(countdown%60).padStart(2,"0");
  if(currentEl)currentEl.textContent=current?current.time:"운행 전";
  if(counterEl)counterEl.textContent=`${hh}:${mm}:${ss}`;'''
if text.count(old_counter) != 1:
    raise RuntimeError("Rev83 elapsed counter block was not found exactly once")
text = text.replace(old_counter, new_counter, 1)

index.write_text(text, encoding="utf-8")

sw = root / "sw.js"
if not sw.exists():
    raise RuntimeError("sw.js is missing")
sw_text = sw.read_text(encoding="utf-8")
sw_text = re.sub(r'const CACHE_NAME="[^"]+";', 'const CACHE_NAME="1560-timetable-rev84-v1";', sw_text)
sw_text = re.sub(r'const REVISION="[^"]+";', 'const REVISION="84";', sw_text)
sw.write_text(sw_text, encoding="utf-8")
