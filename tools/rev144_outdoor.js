/* Current-location outdoor weather. No fixed-city fallback or stored location. */
(() => {
  const button = document.getElementById('outdoorTempBtn');
  const value = document.getElementById('outdoorTempValue');
  const modal = document.getElementById('outdoorTempDialog');
  const message = document.getElementById('outdoorTempMessage');
  const update = document.getElementById('outdoorTempUpdate');
  const refresh = document.getElementById('outdoorTempRefresh');
  let busy = false, last = null, denied = false;
  const TEN_MINUTES = 10 * 60 * 1000;
  function state(text, detail, stamp = '') {
    value.textContent = text;
    message.textContent = detail;
    update.textContent = stamp;
    button.setAttribute('aria-label', '현재 위치 외부 온도 ' + text + ' · 자세히 보기');
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
        state(last.text, last.detail, last.stamp);
        return;
      }
      state('불러오는 중', '현재 위치의 외부 온도를 불러오고 있습니다.');
      controller = new AbortController();
      timeout = setTimeout(() => controller.abort(), 12000);
      const query = new URLSearchParams({latitude: coords.latitude.toFixed(3), longitude: coords.longitude.toFixed(3),
        current: 'temperature_2m', temperature_unit: 'celsius', timeformat: 'unixtime', timezone: 'auto', forecast_days: '1'});
      const response = await fetch('https://api.open-meteo.com/v1/forecast?' + query,
        {signal: controller.signal, cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer'});
      if (!response.ok) throw new Error('weather response');
      const data = await response.json();
      const current = data.current;
      if (!current || !Number.isFinite(current.temperature_2m) || !Number.isFinite(current.time)
        || data.current_units?.temperature_2m !== '°C'
        || Math.abs(Date.now() - current.time * 1000) > 90 * 60 * 1000) throw new Error('invalid or stale weather');
      const text = Math.round(current.temperature_2m) + '°C';
      const detail = '현재 위치 주변의 외부 온도 ' + current.temperature_2m.toFixed(1) + '°C';
      const time = new Intl.DateTimeFormat('ko-KR', {hour: '2-digit', minute: '2-digit', hour12: false,
        timeZone: data.timezone || 'Asia/Seoul'}).format(new Date(current.time * 1000));
      const stamp = '날씨 기준 ' + time + ' · 위치와 온도 자동 갱신';
      last = {coords: {latitude: coords.latitude, longitude: coords.longitude}, fetched: Date.now(), text, detail, stamp};
      state(text, detail, stamp);
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
