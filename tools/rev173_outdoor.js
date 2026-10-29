/* KMA observations only. Position stays in this browser. */
(() => {
  function weatherCondition(code, isDay) {
    const sun = '<g stroke="#c87900" stroke-width="2.5" stroke-linecap="round"><path d="M24 3v5m0 32v5M3 24h5m32 0h5M9 9l4 4m22 22 4 4M9 39l4-4m22-22 4-4"/><circle cx="24" cy="24" r="11" fill="#ffe45c"/></g>';
    const moon = '<path d="M33 5a19 19 0 1 0 10 28A18 18 0 0 1 33 5Z" fill="#fff3a3" stroke="#a07720" stroke-width="2"/>';
    const cloud = '<path d="M12 35h25a8 8 0 0 0 0-16 12 12 0 0 0-23-3A10 10 0 0 0 12 35Z" fill="#fff" stroke="#5687ae" stroke-width="2.5"/>';
    let art, label;
    if (!Number.isInteger(code)) return {svg:'', label:''};
    if (code === 0 || code === 1 || code === 2) {
      if (isDay !== 0 && isDay !== 1) return {svg:'', label:''};
      art = isDay ? sun : moon;
      label = code === 0 ? '맑음' : code === 1 ? '대체로 맑음' : '구름 조금';
      if (!isDay) label += ' · 밤';
      if (code === 2) art = '<g transform="translate(-3 -5) scale(.85)">' + art + '</g>' + cloud;
    } else if (code === 3) { art = cloud; label = '흐림';
    } else if ([45,48].includes(code)) {
      art = cloud + '<path d="M6 40h36M11 45h28" stroke="#6689a7" stroke-width="3" stroke-linecap="round"/>'; label = '안개';
    } else if ([51,53,55,56,57,61,63,65,66,67,80,81,82].includes(code)) {
      art = cloud + '<path d="m15 39-3 6m14-6-3 6m14-6-3 6" stroke="#1261d2" stroke-width="3" stroke-linecap="round"/>'; label = '비';
    } else if ([71,73,75,77,85,86].includes(code)) {
      art = cloud + '<g fill="#205fad"><circle cx="13" cy="42" r="2.5"/><circle cx="25" cy="44" r="2.5"/><circle cx="37" cy="41" r="2.5"/></g>'; label = '눈';
    } else if ([95,96,97,99].includes(code)) {
      art = cloud + '<path d="m25 32-9 9h8l-3 7 13-12h-9l3-4Z" fill="#ffcd19" stroke="#9d6500" stroke-width="1"/>'; label = '뇌우';
    } else return {svg:'', label:''};
    return {svg:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" focusable="false">' + art + '</svg>', label};
  }
  const button = document.getElementById('outdoorTempBtn');
  const value = document.getElementById('outdoorTempValue');
  const icon = document.getElementById('outdoorWeatherIcon');
  const MAX_AGE = 45 * 60 * 1000;
  let busy = false, retryTimer = null, failures = 0, problem = '';
  let dataRequest = null;
  let snapshot = null, lastFetch = 0;
  try { snapshot = JSON.parse(document.getElementById('kmaInitialSnapshot')?.textContent || 'null'); } catch (_) {}
  function fresh(time, maxAge = MAX_AGE) {
    const age = Date.now() - time;
    return Number.isFinite(time) && age >= -5 * 60 * 1000 && age <= maxAge;
  }
  // Cache public observations only. GPS coordinates never enter storage.
  try {
    const cached = JSON.parse(localStorage.getItem('1560-kma-observations-v1') || 'null');
    if (validSnapshot(cached) && (!validSnapshot(snapshot) || cached.fetchedAt > snapshot.fetchedAt)) snapshot = cached;
  } catch (_) {}
  function distance(a, b) {
    const rad = Math.PI / 180;
    const x = (a.longitude - b.longitude) * Math.cos((a.latitude + b.latitude) * rad / 2);
    return Math.hypot(x, a.latitude - b.latitude) * 111;
  }
  function validPoint(point) {
    return Number.isFinite(point.latitude) && Math.abs(point.latitude) <= 90
      && Number.isFinite(point.longitude) && Math.abs(point.longitude) <= 180;
  }
  function nearest(records, coords, maxAge, maxKm) {
    return records.filter(row => validPoint(row) && fresh(row.observedAt, maxAge))
      .map(row => ({...row, km:distance(coords, row)})).filter(row => row.km <= maxKm)
      .sort((a,b) => a.km - b.km)[0];
  }
  function isDay(coords) {
    // Solar elevation, including the usual sunrise/sunset refraction allowance.
    const now = new Date(), rad = Math.PI / 180;
    const day = (Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate()) - Date.UTC(now.getUTCFullYear(),0,0)) / 86400000;
    const hour = now.getUTCHours() + now.getUTCMinutes() / 60;
    const g = 2 * Math.PI / 365 * (day - 1 + (hour - 12) / 24);
    const eq = 229.18 * (.000075 + .001868*Math.cos(g) - .032077*Math.sin(g) - .014615*Math.cos(2*g) - .040849*Math.sin(2*g));
    const dec = .006918 - .399912*Math.cos(g) + .070257*Math.sin(g) - .006758*Math.cos(2*g) + .000907*Math.sin(2*g) - .002697*Math.cos(3*g) + .00148*Math.sin(3*g);
    const angle = (((hour*60 + 4*coords.longitude + eq) % 1440) / 4 - 180) * rad;
    return Math.sin(coords.latitude*rad)*Math.sin(dec) + Math.cos(coords.latitude*rad)*Math.cos(dec)*Math.cos(angle) > Math.sin(-.833*rad) ? 1 : 0;
  }
  function conditionFor(description, coords) {
    let code;
    if (/뇌|천둥|번개/.test(description)) code = 95;
    else if (/눈|진눈깨비/.test(description)) code = 73;
    else if (/비|소나기|이슬비/.test(description)) code = 61;
    else if (/안개|박무|연무/.test(description)) code = 45;
    else if (/흐림/.test(description)) code = 3;
    else if (/구름많음/.test(description)) code = 2;
    else if (/구름조금/.test(description)) code = 1;
    else if (/맑음/.test(description)) code = 0;
    return weatherCondition(code, isDay(coords));
  }
  function state(text, detail, condition) {
    value.textContent = text;
    icon.innerHTML = condition?.svg || '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" focusable="false"><path d="M18 29V10a6 6 0 0 1 12 0v19a10 10 0 1 1-12 0Z" fill="#fff" stroke="#286290" stroke-width="3"/><path d="M24 15v19" stroke="#e54848" stroke-width="5" stroke-linecap="round"/><circle cx="24" cy="37" r="5" fill="#e54848"/></svg>';
    icon.hidden = false;
    const action = problem ? ' · 눌러서 원인 확인 및 다시 시도' : ' · 기상청 날씨누리 열기, 새 창';
    button.title = detail + action;
    button.setAttribute('aria-label', detail + action);
    button.setAttribute('aria-haspopup', problem ? 'dialog' : 'false');
  }
  function usablePosition(position) {
    const coords = position.coords;
    return validPoint(coords) && Number.isFinite(coords.accuracy) && coords.accuracy >= 0 && coords.accuracy <= 5000
      && fresh(position.timestamp,60000);
  }
  function locate(options) {
    return new Promise((resolve,reject) => {
      if (!navigator.geolocation) return reject({code:0});
      navigator.geolocation.getCurrentPosition(resolve,reject,
        options);
    });
  }
  async function quickPosition() {
    try {
      const position = await locate({enableHighAccuracy:false,maximumAge:60000,timeout:2500});
      if (usablePosition(position)) return position;
    } catch (error) { if (error.code === 1 || error.code === 0) throw error; }
    const position = await locate({enableHighAccuracy:true,maximumAge:30000,timeout:5000});
    if (!usablePosition(position)) throw {code:'position'};
    return position;
  }
  function validSnapshot(data) {
    return data?.schema === 1 && data.source === '기상청 날씨누리' && fresh(data.fetchedAt)
      && Array.isArray(data.stations) && Array.isArray(data.conditions);
  }
  async function downloadSnapshot() {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(),12000);
    try {
      const response = await fetch('https://timetable-kma-feed.gusibzo.chatgpt.site/api/kma',
        {signal:controller.signal,cache:'no-store',credentials:'omit'});
      if (!response.ok) throw Error('KMA snapshot unavailable');
      const data = await response.json();
      if (!validSnapshot(data)) throw {code:'stale'};
      snapshot = data; lastFetch = Date.now();
      try { localStorage.setItem('1560-kma-observations-v1',JSON.stringify(data)); } catch (_) {}
      return data;
    } finally { clearTimeout(timer); }
  }
  function fetchSnapshot() {
    if (!dataRequest) dataRequest = downloadSnapshot().finally(() => { dataRequest = null; });
    return dataRequest;
  }
  function getSnapshot() {
    // The snapshot arrives with the page. There is no second network wait on
    // a normal startup; it is still checked against its real observation time.
    if (validSnapshot(snapshot)) return Promise.resolve(snapshot);
    return fetchSnapshot();
  }
  async function load(forceRefresh = false) {
    if (busy || document.hidden) return;
    busy = true;
    if (retryTimer) { clearTimeout(retryTimer); retryTimer = null; }
    try {
      if (!value.textContent.endsWith('°C') || value.textContent === '--°C') state('--°C','기상청 기온과 현재 위치를 확인하고 있습니다');
      const [position,initialData] = await Promise.all([quickPosition(),getSnapshot()]);
      let data = initialData;
      const coords = position.coords;
      let station = nearest(data.stations.filter(row => Number.isFinite(row.temperature) && row.temperature >= -60 && row.temperature <= 60),coords,MAX_AGE,30);
      if (!station) {
        data = await fetchSnapshot();
        station = nearest(data.stations.filter(row => Number.isFinite(row.temperature) && row.temperature >= -60 && row.temperature <= 60),coords,MAX_AGE,30);
      }
      if (!station) throw Error('No recent nearby KMA observation');
      const sky = nearest(data.conditions,coords,90*60*1000,70);
      const condition = sky ? conditionFor(sky.description,coords) : null;
      const time = new Intl.DateTimeFormat('ko-KR',{hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Asia/Seoul'}).format(new Date(station.observedAt));
      const text = station.temperature.toFixed(1) + '°C';
      const detail = '기상청 관측 기온 ' + text + ' · ' + station.name + ' 관측소 · ' + time + ' 관측 · 현재 위치에서 약 ' + station.km.toFixed(1) + 'km'
        + (sky && condition?.label ? ' · 날씨 그림: ' + sky.name + ' ' + sky.description : '');
      problem = ''; failures = 0;
      button.dataset.weatherState = 'ready';
      state(text,detail,condition);
      if (forceRefresh === true || Date.now() - lastFetch >= 300000) fetchSnapshot().then(() => { if (!busy) load(); }).catch(() => {});
    } catch (error) {
      button.dataset.weatherState = error.code === 1 ? 'permission' : 'unavailable';
      problem = error.code === 1 ? '휴대폰의 위치를 켜고, 브라우저 주소 옆 사이트 설정에서 위치 권한을 허용해 주세요.'
        : error.code === 'position' || [0,2,3].includes(error.code) ? '현재 위치를 받지 못했어요. 휴대폰의 위치를 켠 뒤 다시 확인해 주세요.'
        : '기상청 기온을 아직 받지 못했어요. 연결을 확인한 뒤 다시 시도해 주세요.';
      const explanation = document.getElementById('weatherProblemText');
      if (explanation) explanation.textContent = problem;
      // Recover transient failures before the regular five-minute refresh.
      if (error.code !== 1 && ++failures <= 2) retryTimer = setTimeout(() => { retryTimer = null; load(true); }, failures * 15000);
      state('--°C', error.code === 1 ? '휴대폰과 이 사이트의 정확한 위치 권한을 허용해 주세요'
        : error.code === 'position' || [0,2,3].includes(error.code) ? '현재 위치를 확인하지 못했습니다. 위치 설정을 확인해 주세요'
        : error.code === 'stale' ? '기상청 자료의 자동 갱신을 기다리고 있습니다. 잠시 후 다시 확인합니다'
        : '가까운 기상청 관측소의 최신 자료를 받지 못했습니다. 잠시 후 다시 확인합니다');
    } finally {
      busy = false;
    }
  }
  button.addEventListener('click', event => {
    if (!problem || event.button > 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const dialog = document.getElementById('weatherProblem');
    const text = document.getElementById('weatherProblemText');
    if (text) text.textContent = problem;
    if (dialog && !dialog.open) dialog.showModal();
  });
  document.getElementById('weatherTryAgain')?.addEventListener('click', () => {
    document.getElementById('weatherProblem')?.close();
    failures = 0; load(true);
  });
  document.getElementById('weatherProblemClose')?.addEventListener('click', () => document.getElementById('weatherProblem')?.close());
  load();
  setInterval(() => load(true),5*60*1000);
  document.addEventListener('visibilitychange',() => {if (!document.hidden) load();});
  window.addEventListener('pageshow',load);
  window.addEventListener('online',load);
})();
