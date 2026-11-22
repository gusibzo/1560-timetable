(() => {
  "use strict";
  const byId = id => document.getElementById(id);
  const film = byId("film");
  const ctx = film.getContext("2d", {alpha: false});
  const start = byId("start"), stop = byId("stop"), save = byId("save"), status = byId("status");
  const urls = {A: "2NzYyMzQwMDA4ODQ0NDkw4", B: "5NDYzMjMyMjgwMDA0MzM2MDUzNg5"};
  const pad = n => String(n).padStart(2, "0");
  const day = d => d.getFullYear() + "." + pad(d.getMonth() + 1) + "." + pad(d.getDate());
  const time = d => [d.getHours(), d.getMinutes(), d.getSeconds()].map(pad).join(":");
  const clock = d => day(d) + " (" + "일월화수목금토"[d.getDay()] + ") " + time(d);
  const observedTime = new Intl.DateTimeFormat("ko-KR", {timeZone: "Asia/Seoul", month: "numeric",
    day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23"});
  const top = 140, rowHeight = 92, visible = film.height - top;
  const supported = !!(window.MediaRecorder && film.captureStream);
  let route, data, active, blobUrl, generation = 0;
  const entry = new URL(location.href);
  let autoStart = entry.searchParams.get("start") === "1";
  if (autoStart) {
    entry.searchParams.delete("start");
    history.replaceState(null, "", entry);
  }

  function label(value, x, y, size, color, weight = 500, maxWidth) {
    ctx.font = weight + " " + size + "px system-ui,sans-serif";
    ctx.fillStyle = color;
    if (maxWidth) ctx.fillText(value, x, y, maxWidth);
    else ctx.fillText(value, x, y);
  }

  function snapshot(now) {
    const obs = data.observation;
    const age = obs ? now - Date.parse(obs.at) : NaN;
    return Number.isFinite(age) && age >= -60000 && age < 15 * 60000 ? obs : null;
  }

  function draw(offset = 0, observation = data && snapshot(Date.now())) {
    ctx.fillStyle = "#ffffff"; ctx.fillRect(0, 0, film.width, film.height);
    ctx.fillStyle = "#142e49"; ctx.fillRect(0, 0, film.width, top);
    label("1560" + route, 22, 51, 41, "white", 850);
    label(clock(new Date()), 188, 49, 28, "white", 700, 428);
    if (!data) return;
    label("경기버스정보  ·  " + data.stops.length + "개 정류장", 24, 88, 24, "#dce9f6", 650);
    let observationText = "차량 위치 갱신 대기";
    if (observation) {
      observationText = "차량 위치  " + observedTime.format(new Date(observation.at)) + " 기준";
      if (!observation.buses.length) observationText += "  ·  조회 차량 없음";
    }
    label(observationText, 24, 121, 21, "#c8e9ee", 550);
    ctx.save(); ctx.beginPath(); ctx.rect(0, top, film.width, visible); ctx.clip();
    const first = Math.floor(offset / rowHeight);
    for (let i = first; i < data.stops.length; i++) {
      const station = data.stops[i], y = top + i * rowHeight - offset;
      if (y >= film.height) break;
      const buses = observation ? observation.buses.filter(b => b.seq === station.seq) : [];
      ctx.fillStyle = buses.length ? "#e5f5ee" : i % 2 ? "#f3f6fa" : "#fff";
      ctx.fillRect(0, y, film.width, rowHeight);
      const middle = y + rowHeight / 2;
      ctx.fillStyle = "#90adbe";
      ctx.fillRect(41, i === 0 ? middle : y, 4, (i === 0 || i === data.stops.length - 1) ? rowHeight / 2 : rowHeight);
      ctx.beginPath(); ctx.arc(43, middle, 11, 0, Math.PI * 2);
      ctx.fillStyle = station.turn ? "#b33c38" : buses.length ? "#13735a" : "#47758e"; ctx.fill();
      label(station.name, 78, y + 40, 28, "#102e43", 750, buses.length ? 420 : 544);
      const info = [station.seq + "번째", station.area, station.number, station.turn ? "회차" : ""].filter(Boolean);
      label(info.join("  ·  "), 79, y + 72, 20, "#4e6879", 500, 423);
      if (buses.length) {
        label(buses.length === 1 && buses[0].vehicle ? buses[0].vehicle + "호" : buses.length + "대",
          511, y + 40, 25, "#09563f", 800, 113);
        const seats = buses[0].seats;
        label(buses.length === 1 && Number.isInteger(seats) && seats >= 0 ? "빈자리 " + seats : "차량 위치",
          511, y + 69, 18, "#236751", 600, 112);
      }
    }
    ctx.restore();
  }

  async function loadRoute(refresh = false) {
    if (active) return;
    const selected = location.hash === "#record-B" ? "B" : "A";
    const ticket = ++generation;
    if (!refresh || selected !== route) {
      route = selected; data = null; start.disabled = true; status.textContent = "노선을 불러오는 중입니다.";
      for (const key of Object.keys(urls)) byId("record-" + key).setAttribute("aria-current", String(key === route));
      byId("official").href = "https://m.gbis.go.kr/routeBusLocation/" + urls[route];
      draw();
    }
    try {
      const response = await fetch("./route-video-data/" + selected + ".json", {cache: "no-cache"});
      if (!response.ok) throw Error();
      const value = await response.json();
      if (value.route !== selected || !Array.isArray(value.stops) || value.stops.length < 2) throw Error();
      if (ticket !== generation || active) return;
      data = value; draw(); start.disabled = !supported;
      if (!refresh || !save.href) status.textContent = supported ? "녹화 시작을 누르면 맨 위부터 자동으로 내려갑니다." : "이 브라우저는 영상 저장을 지원하지 않습니다. Chrome에서 열어 주세요.";
      if (autoStart) {
        autoStart = false;
        if (supported) record();
      }
    } catch {
      if (ticket === generation && !data) status.textContent = "노선을 불러오지 못했습니다. 다시 열어 주세요.";
    }
  }

  function finish(message) {
    if (!active || active.finishing) return;
    active.finishing = true; active.message = message;
    cancelAnimationFrame(active.frame); stop.disabled = true; status.textContent = "영상을 준비하고 있습니다.";
    if (active.recorder.state !== "inactive") active.recorder.stop();
  }

  function record() {
    if (!data || active || !supported) return;
    const stamp = new Date();
    const observation = snapshot(+stamp);
    draw(0, observation);
    let stream, recorder;
    try {
      stream = film.captureStream(24);
      const types = ["video/mp4;codecs=avc1.42001E", "video/mp4", "video/webm;codecs=vp8", "video/webm", ""];
      for (const mimeType of types) {
        if (mimeType && !MediaRecorder.isTypeSupported(mimeType)) continue;
        try {
          recorder = new MediaRecorder(stream, mimeType ? {mimeType, videoBitsPerSecond: 2600000} : {});
          recorder.start(1000); break;
        } catch { recorder = null; }
      }
      if (!recorder) throw Error();
    } catch {
      stream?.getTracks().forEach(track => track.stop());
      status.textContent = "이 브라우저에서 녹화를 시작하지 못했습니다. Chrome에서 다시 열어 주세요."; return;
    }
    const chunks = [];
    const run = active = {recorder, frame: 0, failed: false, message: "녹화가 끝났습니다."};
    const selected = route;
    if (navigator.wakeLock) navigator.wakeLock.request("screen").then(lock => {
      if (active === run) run.wakeLock = lock;
      else lock.release().catch(() => {});
    }).catch(() => {});
    recorder.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
    recorder.onerror = () => { run.failed = true; finish("영상 저장에 실패했습니다."); };
    recorder.onstop = () => {
      cancelAnimationFrame(run.frame); stream.getTracks().forEach(track => track.stop());
      run.wakeLock?.release().catch(() => {});
      active = null; stop.hidden = true; start.hidden = false; document.querySelector("nav").inert = false;
      if (!run.failed && chunks.length) {
        const blob = new Blob(chunks, {type: recorder.mimeType || chunks[0].type});
        if (blobUrl) URL.revokeObjectURL(blobUrl);
        blobUrl = URL.createObjectURL(blob); save.href = blobUrl;
        const name = "1560" + selected;
        save.download = name + "_" + day(stamp).replaceAll(".", "") + "_" + time(stamp).replaceAll(":", "") +
          (blob.type.includes("mp4") ? ".mp4" : ".webm");
        save.textContent = name + " 영상 저장"; save.hidden = false;
        status.textContent = run.message + " 영상 저장을 눌러 주세요.";
      } else { status.textContent = "저장할 영상이 없습니다. 다시 녹화해 주세요."; }
      draw();
      if (location.hash === "#record-" + (selected === "A" ? "B" : "A")) loadRoute();
    };
    document.querySelector("nav").inert = true; start.hidden = true; stop.hidden = false; stop.disabled = false;
    status.textContent = "녹화 중에는 이 화면을 켜 두세요. 마지막 정류장에서 자동으로 끝납니다.";
    const begin = performance.now(), bottom = Math.max(0, data.stops.length * rowHeight - visible);
    function tick(now) {
      const elapsed = now - begin;
      draw(Math.min(bottom, Math.max(0, elapsed - 1000) * 0.112), observation);
      if (elapsed >= 2000 + bottom / 0.112) finish("마지막 정류장까지 녹화했습니다.");
      else run.frame = requestAnimationFrame(tick);
    }
    run.frame = requestAnimationFrame(tick);
  }
  start.addEventListener("click", record);
  stop.addEventListener("click", () => finish("여기까지 녹화했습니다."));
  window.addEventListener("hashchange", () => loadRoute());
  document.addEventListener("visibilitychange", () => { if (document.hidden) finish("화면 전환 전까지 녹화했습니다."); });
  setInterval(() => { if (data && !active && !document.hidden) draw(); }, 1000);
  setInterval(() => { if (!document.hidden) loadRoute(true); }, 60000);
  loadRoute();
})();
