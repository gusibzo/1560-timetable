(() => {
  "use strict";
  const byId = id => document.getElementById(id);
  const film = byId("film");
  const ctx = film.getContext("2d", {alpha: false});
  const start = byId("start"), stop = byId("stop"), save = byId("save"), status = byId("status");
  const urls = {A: "2NzYyMzQwMDA4ODQ0NDkw4", B: "5NDYzMjMyMjgwMDA0MzM2MDUzNg5"};
  const busFeed = "https://timetable-kma-feed.gusibzo.chatgpt.site/api/gbis/";
  const pad = n => String(n).padStart(2, "0");
  const day = d => d.getFullYear() + "." + pad(d.getMonth() + 1) + "." + pad(d.getDate());
  const time = d => [d.getHours(), d.getMinutes(), d.getSeconds()].map(pad).join(":");
  const clock = d => day(d) + " (" + "일월화수목금토"[d.getDay()] + ") " + time(d);
  const observedTime = new Intl.DateTimeFormat("ko-KR", {timeZone: "Asia/Seoul", month: "numeric",
    day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23"});
  const listTop = 372, rowHeight = 128, visible = film.height - listTop;
  const rail = 220, nameX = 282;
  const outbound = "#375fcd", inbound = "#cd4779", ink = "#17202b";
  // Measured on the supplied 720 px wide recording: about 243 px per second.
  const pixelsPerSecond = 243;
  const supported = !!(window.MediaRecorder && film.captureStream);
  let route, data, turnIndex, blobUrl, active, loading, generation = 0;
  const entry = new URL(location.href);
  let autoStart = entry.searchParams.get("start") === "1";
  if (autoStart) {
    entry.searchParams.delete("start");
    history.replaceState(null, "", entry);
  }

  function rect(x, y, w, h, color, radius = 0) {
    ctx.fillStyle = color;
    if (!radius) { ctx.fillRect(x, y, w, h); return; }
    ctx.beginPath(); ctx.roundRect(x, y, w, h, radius); ctx.fill();
  }

  function label(value, x, y, size, color = ink, weight = 500, align = "left") {
    ctx.font = weight + " " + size + "px system-ui,Noto Sans KR,Noto Sans CJK KR,sans-serif";
    ctx.textAlign = align; ctx.fillStyle = color; ctx.fillText(value, x, y);
  }

  function pill(x, y, w, h, fill, text, size, color) {
    rect(x, y, w, h, fill, h / 2);
    label(text, x + w / 2, y + h / 2 + size * 0.34, size, color, 700, "center");
  }

  function snapshot(now, obs = data?.observation) {
    const age = obs ? now - Date.parse(obs.at) : NaN;
    return Array.isArray(obs?.buses) && Number.isFinite(age) && age >= -60000 && age < 15 * 60000 ? obs : null;
  }

  function seatLabel(bus) {
    return Number.isInteger(bus.seats) && bus.seats >= 0 ? bus.seats + "석" : "미제공";
  }

  const seatColors = {
    green: {fill: "#d5f1cf", text: "#204f26", heading: "#165532"},
    pink: {fill: "#f6a7cf", text: "#741343", heading: "#ad226d"},
    red: {fill: "#be2030", text: "#ffffff", heading: "#be2030"},
    unknown: {fill: "#eef1f5", text: "#414c5a", heading: "#414c5a"}
  };

  function seatColor(seats) {
    if (!Number.isInteger(seats) || seats < 0) return seatColors.unknown;
    if (seats <= 10) return seatColors.red;
    if (seats <= 20) return seatColors.pink;
    return seatColors.green;
  }

  function drawHeading(now, observation, bus) {
    const center = film.width / 2;
    rect(0, 0, film.width, 144, "#f2f4f8");
    label("버스 위치", center, 54, 36, ink, 700, "center");
    label(clock(now), center, 115, 42, ink, 700, "center");
    pill(center - 175, 169, 130, 46, "#fae7eb", "직행좌석", 27, "#aa1936");
    label("1560" + route, center - 26, 207, 51, "#b51336", 800);
    if (!data) return;
    const buses = observation?.buses || [];
    if (bus) {
      const number = bus.vehicle ? bus.vehicle + "호" : "번호 미상";
      const prefix = "운행 " + buses.length + "대  ·  " + number + "  ·  ";
      const seats = "잔여 " + seatLabel(bus);
      ctx.font = "700 34px system-ui,Noto Sans KR,Noto Sans CJK KR,sans-serif";
      const left = center - ctx.measureText(prefix + seats).width / 2;
      label(prefix, left, 256, 34, "#165532", 700);
      label(seats, left + ctx.measureText(prefix).width, 256, 34, seatColor(bus.seats).heading, 700);
    } else if (buses.length) {
      label("운행 " + buses.length + "대", center, 256, 34, "#165532", 700, "center");
    } else {
      label(data.regions || "서울, 수원, 용인", center, 254, 30, ink, 600, "center");
    }
    let source = "경기버스정보 · 차량 위치 갱신 대기";
    if (observation) {
      source = "경기버스정보 · " + observedTime.format(new Date(observation.at)) + " 기준";
      if (!observation.buses.length) source += " · 운행 차량 없음";
    }
    label(source, center, 295, 23, "#4e5a67", 500, "center");
    const directions = data.directions || ["신분당선강남역(중)", "경희대학교"];
    rect(0, 312, film.width, 2, "#e0e3e8");
    directions.forEach((direction, i) => {
      label(direction + " 방면", center * (i + 0.5), 353, 27, ink, 500, "center");
      rect(i * center, listTop - 7, center, 7, i ? "#f0a0bc" : "#9ebdf5");
    });
  }

  function busSymbol(x, y) {
    rect(x + 4, y + 38, 9, 12, "#9a1630", 3);
    rect(x + 33, y + 38, 9, 12, "#9a1630", 3);
    rect(x, y, 46, 44, "#c41638", 9);
    rect(x + 5, y + 6, 36, 22, "#eff7ff", 4);
    rect(x + 5, y + 34, 9, 4, "#fff5bb", 2);
    rect(x + 32, y + 34, 9, 4, "#fff5bb", 2);
  }

  function vehicle(bus, middle) {
    busSymbol(151, middle - 25);
    const color = seatColor(bus.seats);
    pill(29, middle - 33, 114, 37, color.fill, seatLabel(bus), 29, color.text);
    label(bus.vehicle || "번호 미상", 86, middle + 32, 29, ink, 700, "center");
  }

  function stopMarker(middle, color, endpoint) {
    if (endpoint) {
      rect(rail - 15, middle - 15, 30, 30, color, 7);
      ctx.beginPath(); ctx.arc(rail, middle, 6, 0, 2 * Math.PI); ctx.fillStyle = "white"; ctx.fill();
      return;
    }
    ctx.beginPath(); ctx.arc(rail, middle, 14, 0, 2 * Math.PI);
    ctx.fillStyle = "white"; ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(rail - 8, middle - 3);
    ctx.lineTo(rail, middle + 6); ctx.lineTo(rail + 8, middle - 3);
    ctx.lineWidth = 3.5; ctx.lineJoin = "round"; ctx.stroke();
  }

  function stopName(name, x, y, passing) {
    ctx.font = "600 35px system-ui,Noto Sans KR,Noto Sans CJK KR,sans-serif";
    const width = film.width - x - 20;
    let display = name;
    if (ctx.measureText(display).width > width) {
      while (display && ctx.measureText(display + "…").width > width) display = display.slice(0, -1);
      display += "…";
    }
    label(display, x, y, 35, passing ? "#697481" : ink, 600);
  }

  // Compute the exact markers painted in this frame once. The heading must
  // reference a visible marker, including when several buses share a stop.
  function visibleRows(offset, observation) {
    const rows = [];
    if (!data) return rows;
    const busesByStop = new Map();
    for (const bus of observation?.buses || []) {
      if (!busesByStop.has(bus.seq)) busesByStop.set(bus.seq, []);
      busesByStop.get(bus.seq).push(bus);
    }
    const first = Math.floor(offset / rowHeight);
    for (let i = first; i < data.stops.length; i++) {
      const station = data.stops[i], y = listTop + i * rowHeight - offset;
      if (y >= film.height) break;
      const middle = y + rowHeight / 2;
      const buses = busesByStop.get(station.seq) || [];
      const vehicles = buses.length === 2 ? [
        {bus: buses[0], middle: middle - 30}, {bus: buses[1], middle: middle + 31}
      ] : buses.length ? [{bus: buses[0], middle: middle - (buses.length > 2 ? 17 : 0)}] : [];
      rows.push({station, i, y, middle, vehicles, hiddenCount: buses.length - vehicles.length});
    }
    return rows;
  }

  function draw(offset = 0, observation = snapshot(Date.now())) {
    const rows = visibleRows(offset, observation);
    // Follow the first fully readable bus from the top of the scrolling list.
    // Don't show a vehicle number when its seat badge/number is clipped or offscreen.
    const focused = rows.flatMap(row => row.vehicles).find(({middle}) =>
      middle - 33 >= listTop && middle + 38 <= film.height);
    rect(0, 0, film.width, film.height, "#fff");
    drawHeading(new Date(), observation, focused?.bus);
    if (!data) return;
    ctx.save(); ctx.beginPath(); ctx.rect(0, listTop, film.width, visible); ctx.clip();
    for (const {station, i, y, middle, vehicles, hiddenCount} of rows) {
      const last = i === data.stops.length - 1;
      const color = turnIndex >= 0 && i > turnIndex ? inbound : outbound;
      rect(0, y + rowHeight - 2, film.width, 2, "#e1e4e8");
      if (i > 0) rect(rail - 4.5, y, 9, rowHeight / 2, color);
      if (!last) rect(rail - 4.5, middle, 9, rowHeight / 2, i === turnIndex ? inbound : color);
      stopMarker(middle, color, i === 0 || last || i === turnIndex);

      const passing = station.name.endsWith("(경유)");
      if (station.toilet) pill(nameX, y + 22, 50, 31, "#eef1f5", "WC", 18, "#414c5a");
      stopName(station.name.replace(/\(경유\)$/, "(미정차)"), station.toilet ? nameX + 60 : nameX, y + 53, passing);
      const kind = i === 0 ? "기점" : last ? "종점" : i === turnIndex ? "회차" : "";
      if (kind) pill(nameX, y + 73, 68, 33, color, kind, 22, "#fff");
      label([station.number, station.area].filter(Boolean).join(" | "), nameX + (kind ? 79 : 0),
        y + 99, 29, "#35414e");
      for (const marker of vehicles) vehicle(marker.bus, marker.middle);
      if (hiddenCount) label("외 " + hiddenCount + "대", 113, y + 111, 24, ink, 600, "center");
    }
    ctx.restore();
  }

  async function readJson(url) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 9000);
    try {
      const response = await fetch(url, {cache: "no-store", credentials: "omit", signal: controller.signal});
      if (!response.ok) throw Error();
      return await response.json();
    } finally { clearTimeout(timer); }
  }

  async function loadRoute(wantRecording = false) {
    if (active) return;
    const selected = location.hash === "#record-B" ? "B" : "A";
    const ticket = ++generation;
    if (selected !== route) {
      route = selected; data = null;
      for (const key of Object.keys(urls)) byId("record-" + key).setAttribute("aria-current", String(key === route));
      byId("official").href = "https://m.gbis.go.kr/routeBusLocation/" + urls[route];
      save.hidden = true; save.removeAttribute("href");
      draw();
    }
    loading = true; start.disabled = true;
    status.textContent = "차량 위치와 잔여 좌석을 조회하고 있습니다.";
    const [stations, live] = await Promise.allSettled([
      readJson("./route-video-data/" + selected + ".json"), readJson(busFeed + selected)
    ]);
    if (ticket !== generation) return;
    loading = false;
    const latest = stations.value;
    const routeData = latest?.route === selected && latest.stops?.length > 1 ? latest : data;
    if (!routeData) {
      start.disabled = !supported; start.textContent = "다시 조회";
      status.textContent = "노선을 불러오지 못했습니다. 다시 조회해 주세요."; return;
    }
    const stops = new Map(routeData.stops.map(s => [s.seq, s.id]));
    const candidates = [live.value?.route === selected ? live.value : null, latest?.observation, data?.observation]
      .filter(obs => obs && snapshot(Date.now(), obs) && obs.buses.every(bus =>
        stops.has(bus.seq) && (bus.stationId == null || bus.stationId === stops.get(bus.seq))))
      .sort((a, b) => Date.parse(b.at) - Date.parse(a.at));
    const observation = candidates[0] || null;
    data = {...routeData, observation}; turnIndex = data.stops.findIndex(station => station.turn);
    draw(0, observation);
    const ready = !!observation?.buses.length;
    start.disabled = !supported;
    start.textContent = ready ? "● 녹화 시작" : "차량 다시 조회";
    if (!supported) {
      status.textContent = "이 브라우저는 영상 저장을 지원하지 않습니다. Chrome에서 열어 주세요."; return;
    }
    if (!observation || !ready) {
      status.textContent = observation ? "경기버스정보에 표시된 운행 차량이 0대입니다. 잠시 뒤 다시 조회해 주세요." :
        "최근 차량 정보를 받지 못했습니다. 차량 다시 조회를 눌러 주세요."; return;
    }
    if (wantRecording && !document.hidden) record(observation);
    else status.textContent = "차량 " + observation.buses.length + "대의 위치를 확인했습니다. 녹화 시작을 누르세요.";
  }

  function finish(message) {
    if (!active || active.finishing) return;
    active.finishing = true; active.message = message;
    cancelAnimationFrame(active.frame); stop.disabled = true; status.textContent = "영상을 준비하고 있습니다.";
    if (active.recorder.state !== "inactive") active.recorder.stop();
  }

  function record(observation) {
    if (!data || active || !supported) return;
    const stamp = new Date();
    draw(0, observation);
    let stream, recorder;
    try {
      stream = film.captureStream(30);
      const types = ["video/mp4;codecs=avc1.420020", "video/mp4", "video/webm;codecs=vp8", "video/webm", ""];
      for (const mimeType of types) {
        if (mimeType && !MediaRecorder.isTypeSupported(mimeType)) continue;
        try {
          recorder = new MediaRecorder(stream, mimeType ? {mimeType, videoBitsPerSecond: 4000000} : {});
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
    recorder.onstop = async () => {
      cancelAnimationFrame(run.frame); stream.getTracks().forEach(track => track.stop());
      run.wakeLock?.release().catch(() => {});
      stop.hidden = true;
      if (!run.failed && chunks.length) {
        let blob = new Blob(chunks, {type: recorder.mimeType || chunks[0].type});
        let message = run.message;
        let saveLabel = "영상 저장";
        if (blob.type.includes("mp4")) {
          try {
            const {finalizeRouteMp4} = await import("./route-video-mp4.mjs");
            const result = await finalizeRouteMp4(blob);
            blob = result.blob;
            message += " 영상 길이 " + result.duration.toFixed(1) + "초.";
          } catch {
            message = "카톡용 MP4를 준비하지 못했습니다. 녹화 원본을 저장할 수 있습니다.";
            saveLabel = "녹화 원본 저장";
          }
        }
        if (blobUrl) URL.revokeObjectURL(blobUrl);
        blobUrl = URL.createObjectURL(blob); save.href = blobUrl;
        const name = "1560" + selected;
        save.download = name + "_" + day(stamp).replaceAll(".", "") + "_" + time(stamp).replaceAll(":", "") +
          (blob.type.includes("mp4") ? ".mp4" : ".webm");
        save.textContent = name + " " + saveLabel; save.hidden = false;
        status.textContent = message + " " + saveLabel + "을 눌러 주세요.";
      } else { status.textContent = "저장할 영상이 없습니다. 다시 녹화해 주세요."; }
      active = null; start.hidden = false; document.querySelector("nav").inert = false;
      draw();
      if (location.hash === "#record-" + (selected === "A" ? "B" : "A")) loadRoute();
    };
    save.hidden = true; save.removeAttribute("href");
    document.querySelector("nav").inert = true; start.hidden = true; stop.hidden = false; stop.disabled = false;
    status.textContent = "녹화 중에는 이 화면을 켜 두세요. 마지막 정류장에서 자동으로 끝납니다.";
    const begin = performance.now(), bottom = Math.max(0, data.stops.length * rowHeight - visible);
    function tick(now) {
      const elapsed = Math.max(0, now - begin);
      draw(Math.min(bottom, Math.max(0, elapsed - 900) * pixelsPerSecond / 1000), observation);
      if (elapsed >= 1900 + 1000 * bottom / pixelsPerSecond) finish("마지막 정류장까지 녹화했습니다.");
      else run.frame = requestAnimationFrame(tick);
    }
    run.frame = requestAnimationFrame(tick);
  }
  start.addEventListener("click", () => loadRoute(true));
  stop.addEventListener("click", () => finish("여기까지 녹화했습니다."));
  window.addEventListener("hashchange", () => loadRoute());
  document.addEventListener("visibilitychange", () => { if (document.hidden) finish("화면 전환 전까지 녹화했습니다."); });
  setInterval(() => { if (data && !active && !document.hidden) draw(); }, 1000);
  setInterval(() => { if (!document.hidden && !active && !loading && save.hidden) loadRoute(); }, 60000);
  loadRoute(autoStart);
})();
