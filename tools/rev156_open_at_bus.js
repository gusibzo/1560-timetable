/* Align the current bus row below the sticky header when opening the app. */
(() => {
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  let generation = 0;
  const cancel = () => { generation++; };
  for (const name of ['pointerdown', 'touchstart', 'wheel', 'keydown']) {
    window.addEventListener(name, cancel, {passive:true});
  }

  function alignBusRow() {
    if (document.hidden) return;
    if (typeof rev23SyncCounter === 'function') rev23SyncCounter();
    const marker = document.querySelector('.grid tbody td.next > .time, .grid tbody .next-ext');
    const row = marker && marker.closest('tr');
    const header = document.querySelector('.sticky-head');
    const wrap = document.querySelector('main.wrap');
    if (!row || !header || !wrap) return;

    // Supply only the space needed to align even the final timetable row.
    let space = document.getElementById('rev156-open-space');
    if (!space) {
      space = document.createElement('div');
      space.id = 'rev156-open-space';
      space.setAttribute('aria-hidden', 'true');
      space.style.pointerEvents = 'none';
      wrap.appendChild(space);
    }
    space.style.height = '0px';
    const inset = parseFloat(getComputedStyle(header).top) || 0;
    const headerBottom = inset + header.getBoundingClientRect().height;
    const top = Math.max(0, window.scrollY + row.getBoundingClientRect().top - headerBottom - 8);
    const scroller = document.scrollingElement || document.documentElement;
    const maxScroll = Math.max(0, scroller.scrollHeight - window.innerHeight);
    space.style.height = Math.max(0, Math.ceil(top - maxScroll)) + 'px';
    window.scrollTo({top, left:window.scrollX, behavior:'auto'});
  }

  function onOpen() {
    if (document.hidden) return;
    const current = ++generation;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (current === generation) alignBusRow();
    }));
  }
  window.addEventListener('pageshow', onOpen);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) cancel(); else onOpen();
  });
  if (document.readyState === 'complete') onOpen();
})();
