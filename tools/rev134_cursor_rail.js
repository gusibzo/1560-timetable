/* Keep the raised divider under the row currently pointed to or touched. */
(() => {
  const rows = document.getElementById("rows");
  if (!rows) return;
  let activeIndex = -1;

  function mark(index) {
    if (index === activeIndex && rows.children[index]?.classList.contains("rev134-cursor-row")) return;
    rows.querySelectorAll(".rev134-cursor-row").forEach(row => row.classList.remove("rev134-cursor-row"));
    activeIndex = index;
    if (index >= 0) rows.children[index]?.classList.add("rev134-cursor-row");
  }

  function rowAt(x, y) {
    const row = document.elementFromPoint(x, y)?.closest("#rows > tr");
    return row ? Array.prototype.indexOf.call(rows.children, row) : -1;
  }

  document.addEventListener("pointerdown", event => mark(rowAt(event.clientX, event.clientY)), {passive:true});
  document.addEventListener("pointermove", event => {
    // A finger's last touched row remains marked after release.
    const index = rowAt(event.clientX, event.clientY);
    if (index >= 0 || event.pointerType !== "touch") mark(index);
  }, {passive:true});
  document.addEventListener("touchstart", event => {
    const touch = event.touches[0];
    if (touch) mark(rowAt(touch.clientX, touch.clientY));
  }, {passive:true});
  document.addEventListener("touchmove", event => {
    const touch = event.touches[0];
    if (!touch) return;
    const index = rowAt(touch.clientX, touch.clientY);
    if (index >= 0) mark(index);
  }, {passive:true});
  document.addEventListener("focusin", event => {
    const row = event.target.closest?.("#rows > tr");
    if (row) mark(Array.prototype.indexOf.call(rows.children, row));
  });

  // The timetable rerenders each minute; restore the marker to the same row.
  new MutationObserver(() => {
    if (activeIndex >= 0) rows.children[activeIndex]?.classList.add("rev134-cursor-row");
  }).observe(rows, {childList:true});
})();
