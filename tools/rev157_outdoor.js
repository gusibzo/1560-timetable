/* Current-location outdoor weather. No fixed-city fallback or stored location. */
(() => {
  const button = document.getElementById('outdoorTempBtn');
  const value = document.getElementById('outdoorTempValue');
  const icon = document.getElementById('outdoorWeatherIcon');
  const modal = document.getElementById('outdoorTempDialog');
  const message = document.getElementById('outdoorTempMessage');
  const update = document.getElementById('outdoorTempUpdate');
  const refresh = document.getElementById('outdoorTempRefresh');
  let busy = false, last = null, denied = false;
  const TEN_MINUTES = 10 * 60 * 1000;
  // Open-Meteo WMO codes and daylight come from the same current observation.
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
  function state(text, detail, stamp = '', condition = null) {
    value.textContent = text;
    value.setAttribute('data-status', String(!text.endsWith('°C')));
    icon.innerHTML = condition?.svg || '';
    icon.hidden = !condition?.svg;
    message.textContent = detail;
    update.textContent = stamp;
    button.setAttribute('aria-label', '현재 위치 외부 온도 ' + text + (condition?.label ? ' · ' + condition.label : '') + ' · 자세히 보기');
    button.title = detail;
  }
  function distance(a, b) {
    const rad = Math.PI / 180;
    const x = (a.longitude - b.longitude) * Math.cos((a.latitude + b.latitude) * rad / 2);
    return Math.hypot(x, a.latitude - b.latitude) * 111;
  }
  function locate() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) return reject({code: 0});
      navigator.geolocation.getCurrentPosition(resolve, reject,
        {enableHighAccuracy: false, maximumAge: 30000, timeout: 15000});
    });
  }
  async function load(force = false) {
    if (busy || document.hidden || (denied && !force)) return;
    busy = true;
    refresh.disabled = true;
    let controller, timeout;
    try {
      // Clear the previous temperature until the current position is known.
      state('확인 중', '현재 위치를 확인하고 있습니다.');
      const position = await locate();
      const coords = position.coords;
      if (!Number.isFinite(coords.latitude) || !Number.isFinite(coords.longitude)) throw {code: 2};
      denied = false;
      const now = Date.now();
      if (!force && last && now - last.fetched < TEN_MINUTES && distance(coords, last.coords) < 2) {
        state(last.text, last.detail, last.stamp, last.condition);
        return;
      }
      state('불러오는 중', '현재 위치의 외부 온도를 불러오고 있습니다.');
      controller = new AbortController();
      timeout = setTimeout(() => controller.abort(), 12000);
      const query = new URLSearchParams({latitude: coords.latitude.toFixed(3), longitude: coords.longitude.toFixed(3),
        current: 'temperature_2m,weather_code,is_day', temperature_unit: 'celsius', timeformat: 'unixtime', timezone: 'auto', forecast_days: '1'});
      const response = await fetch('https://api.open-meteo.com/v1/forecast?' + query,
        {signal: controller.signal, cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer'});
      if (!response.ok) throw new Error('weather response');
      const data = await response.json();
      const current = data.current;
      if (!current || !Number.isFinite(current.temperature_2m) || !Number.isFinite(current.time)
        || data.current_units?.temperature_2m !== '°C'
        || Math.abs(Date.now() - current.time * 1000) > 90 * 60 * 1000) throw new Error('invalid or stale weather');
      const text = Math.round(current.temperature_2m) + '°C';
      const condition = weatherCondition(current.weather_code, current.is_day);
      const detail = '현재 위치 주변의 외부 온도 ' + current.temperature_2m.toFixed(1) + '°C' + (condition.label ? ' · ' + condition.label : '');
      const time = new Intl.DateTimeFormat('ko-KR', {hour: '2-digit', minute: '2-digit', hour12: false,
        timeZone: data.timezone || 'Asia/Seoul'}).format(new Date(current.time * 1000));
      const stamp = '날씨 기준 ' + time + ' · 위치와 온도 자동 갱신';
      last = {coords: {latitude: coords.latitude, longitude: coords.longitude}, fetched: Date.now(), text, detail, stamp, condition};
      state(text, detail, stamp, condition);
    } catch (error) {
      // Never display an old location's temperature as a current reading.
      last = null;
      if (error.code === 1) {
        denied = true;
        state('위치 허용', '휴대폰의 위치와 이 사이트의 위치 권한을 허용한 뒤 다시 불러오기를 눌러주세요.');
      } else if (error.code === 0) {
        state('지원 안 됨', '이 브라우저에서는 현재 위치를 확인할 수 없습니다.');
      } else if (error.code === 2 || error.code === 3) {
        state('위치 대기', '현재 위치를 확인하지 못했습니다. 위치 설정을 확인한 뒤 다시 불러와주세요.');
      } else {
        state('다시 시도', '날씨 정보를 받지 못했습니다. 인터넷 연결을 확인한 뒤 다시 불러와주세요.');
      }
    } finally {
      clearTimeout(timeout);
      busy = false;
      refresh.disabled = false;
    }
  }
  button.addEventListener('click', () => {
    if (!modal.open) modal.showModal();
  });
  document.getElementById('outdoorTempClose').addEventListener('click', () => modal.close());
  modal.addEventListener('click', event => {
    if (event.target !== modal) return;
    const rect = modal.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) modal.close();
  });
  modal.addEventListener('close', () => button.focus({preventScroll: true}));
  refresh.addEventListener('click', () => load(true));
  setTimeout(() => load(), 800);
  setInterval(() => load(), 2 * 60 * 1000);
  document.addEventListener('visibilitychange', () => {if (!document.hidden) load();});
  window.addEventListener('pageshow', () => load());
  window.addEventListener('online', () => load());
})();
