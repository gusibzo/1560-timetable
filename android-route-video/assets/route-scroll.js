(() => {
  if (window.routeVideo1560) return;
  let current;
  let frame;

  function routeList() {
    if (!/\b1560B\b/.test(document.body.innerText)) return null;
    const row = document.querySelector("[data-index]");
    for (let element = row?.parentElement; element; element = element.parentElement) {
      if (element.clientHeight > 0 && element.scrollHeight - element.clientHeight > 50 &&
          /^(auto|scroll)$/.test(getComputedStyle(element).overflowY)) return element;
    }
    return null;
  }

  function stop() {
    cancelAnimationFrame(frame);
    if (current?.state === "running") current.state = "stopped";
  }

  function rewind() {
    stop();
    const list = routeList();
    if (!list) return false;
    list.scrollTo({top: 0, behavior: "instant"});
    return true;
  }

  function start() {
    if (!rewind()) return false;
    const list = routeList();
    const speed = Math.min(165, Math.max(90, list.clientHeight * 0.27)) / 1000;
    const run = current = {state: "running"};
    const begin = performance.now();
    let position = 0;
    let previous = begin + 900;
    let reachedBottom;

    function tick(now) {
      if (!list.isConnected) {
        run.state = "error";
        return;
      }
      if (now > previous) {
        // Limit jumps when a frame is delayed, and read the virtual list's moving end.
        const bottom = list.scrollHeight - list.clientHeight;
        position = Math.min(bottom, position + Math.min(now - previous, 50) * speed);
        previous = now;
        list.scrollTo({top: position, behavior: "instant"});
        if (bottom <= list.scrollTop + 1) {
          reachedBottom ??= now;
          if (now - reachedBottom >= 850) {
            run.state = "done";
            return;
          }
        } else {
          reachedBottom = undefined;
        }
      }
      frame = requestAnimationFrame(tick);
    }

    frame = requestAnimationFrame(tick);
    return true;
  }

  window.routeVideo1560 = {
    ready: () => routeList() !== null,
    rewind,
    start,
    stop,
    state: () => current?.state ?? "idle"
  };
})();
