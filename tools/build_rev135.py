from pathlib import Path
import re
import runpy
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
base = Path(__file__).with_name("build_rev134.py")
old = sys.argv[:]
try:
    sys.argv = [str(base), str(root)]
    runpy.run_path(str(base), run_name="__main__")
finally:
    sys.argv = old
index = root / "index.html"
text = index.read_text(encoding="utf-8").replace("Rev.134", "Rev.135")
css = Path(__file__).with_name("rev133_row_six_rail.css").read_text(encoding="utf-8")
css = css.replace(".grid tbody#rows > tr:nth-child(6) > td {", ".grid tbody#rows > tr.rev134-cursor-row > td {").replace("/* Raise only the divider between timetable rows 6 and 7. */", "/* Raise the divider under the row at the cursor or touch point. */")
assert text.count(css) == 1
text = text.replace(css, """
/* The raised vertical edge follows the pointed-to column. */
.grid tbody#rows > tr > td.rev135-cursor-column {
  position:relative;
  z-index:1;
  border-right:1px solid var(--row-dot)!important;
}
""", 1)
old_js = Path(__file__).with_name("rev134_cursor_rail.js").read_text(encoding="utf-8")
assert text.count(old_js) == 1
text = text.replace(old_js, """
(() => {
  const rows = document.getElementById("rows");
  if (!rows) return;
  let active = -1;
  function paint() {
    rows.querySelectorAll("td").forEach(cell =>
      cell.classList.toggle("rev135-cursor-column", cell.cellIndex === active));
  }
  function mark(x, y, keep) {
    const cell = document.elementFromPoint(x,y)?.closest("#rows > tr > td");
    if (!cell && keep) return;
    active = cell ? cell.cellIndex : -1;
    paint();
  }
  document.addEventListener("pointerdown", e => mark(e.clientX,e.clientY,false), {passive:true});
  document.addEventListener("pointermove", e => mark(e.clientX,e.clientY,e.pointerType === "touch"), {passive:true});
  document.addEventListener("touchmove", e => {
    const t=e.touches[0]; if(t) mark(t.clientX,t.clientY,true);
  }, {passive:true});
  document.addEventListener("focusin", e => {
    const cell=e.target.closest?.("#rows > tr > td");
    if(cell){active=cell.cellIndex;paint();}
  });
  let day = document.body.dataset.day;
  new MutationObserver(() => {
    if(day !== document.body.dataset.day){day=document.body.dataset.day;active=-1;}
    paint();
  }).observe(rows,{childList:true});
})();
""", 1)
text = text.replace("./sw.js?v=134", "./sw.js?v=135")
index.write_text(text, encoding="utf-8")
sw = root / "sw.js"
s = sw.read_text(encoding="utf-8").replace('1560-timetable-rev134-v1','1560-timetable-rev135-v1').replace('REVISION="134"','REVISION="135"')
sw.write_text(s, encoding="utf-8")
