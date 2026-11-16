import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const root = process.argv[2] || '_site';
const html = readFileSync(root + '/index.html', 'utf8');
const core = html.match(/<script id="trip-records-core">([\s\S]*?)<\/script>/)[1];
const code = html.match(/<script id="rev189-trip-timer">([\s\S]*?)<\/script>/)[1];
assert.equal((html.match(/id="tripTimer"/g) || []).length, 1);
assert.ok(html.indexOf('id="tripTimer"') > html.indexOf('id="roadTrafficBtn"'));
assert.ok(html.indexOf('id="tripTimer"') < html.indexOf('<nav class="switch"'));
assert.ok(html.indexOf('id="rev189-trip-timer"') > html.indexOf('<tbody id="rows">'));
assert.match(html, /class="trip-readout">\s*<p[^>]*>.*id="tripDepartTime".*<\/p>\s*<div[^>]*>\s*<span[^>]*>경과 시간<\/span>\s*<output id="tripElapsed"/);
const key = 'bus1560-trip-timer-v1';
const base = Date.parse('2026-11-10T14:59:50Z'); // 23:59:50 in Korea.
function boot(storage, initial = base, blocked = false, holidays = [], AudioContext) {
  const nodes = new Map(), windowEvents = {}, documentEvents = {};
  let now = initial, interval, nextWatch = 0;
  const watches = new Map();
  const slots = [];
  const probes = [];
  let rebuild;
  const navigator = {geolocation:{
    watchPosition(success, error) { const id = ++nextWatch; watches.set(id, {success, error}); return id; },
    clearWatch(id) { watches.delete(id); },
    getCurrentPosition(success, error) { probes.push({success, error}); }
  }};
  const node = id => {
    if (!nodes.has(id)) nodes.set(id, {textContent:'', dataset:{}, attrs:{}, events:{},
      addEventListener(name, cb) { this.events[name] = cb; },
      setAttribute(name, value) { this.attrs[name] = value; },
      removeAttribute(name) { delete this.attrs[name]; }});
    return nodes.get(id);
  };
  node('rows').querySelectorAll = () => slots;
  class Clock extends Date { static now() { return now; } }
  const doc = {hidden:false, getElementById:node, querySelectorAll:()=>[],
    addEventListener(name, cb) { documentEvents[name] = cb; }};
  const dates = html.match(/<script id="rev141-korea-date">([\s\S]*?)<\/script>/)[1];
  vm.runInNewContext(dates + '\n' + core + '\n' + code, {Date:Clock, document:doc, navigator,
    fetch: async path => ({
      ok:true,
      async arrayBuffer() { return path; }
    }),
    calendarInfo: date => ({holidays: holidays.includes(new Date(date.getTime()+32400000).toISOString().slice(0,10)) ? ['공휴일'] : []}),
    rev92DistanceMetres: (a,b) => Math.hypot((a.latitude-b.latitude)*111195,(a.longitude-b.longitude)*88400),
    MutationObserver: class {
      constructor(callback) { rebuild = callback; }
      observe(target) { assert.equal(target, node('rows')); }
    },
    window:{AudioContext, addEventListener(name, cb) { windowEvents[name] = cb; }},
    localStorage:{getItem(k) { if (blocked) throw Error('blocked'); return storage[k] ?? null; },
      setItem(k, value) { if (blocked) throw Error('blocked'); storage[k] = value; }},
    setInterval(cb) { interval = cb; }});
  return {node, doc, windowEvents, documentEvents, watches, probes,
    slot(time, day = 'weekday') {
      const button = node(day + ' ' + time);
      button.dataset = {tripTime:time, tripDay:day};
      slots.push(button);
      rebuild();
      return button;
    },
    reserve(time, day = 'weekday') {
      documentEvents.click({target:{closest:()=>({dataset:{tripTime:time, tripDay:day}})}});
    },
    fix(latitude, longitude, accuracy = 10, timestamp = now) {
      for (const watch of [...watches.values()]) watch.success({coords:{latitude,longitude,accuracy},timestamp});
    },
    denied() { for (const watch of [...watches.values()]) watch.error({code:1}); },
    at(value) { now = value; interval(); },
    click(id) {
      node(id).events.click();
      const target = node(id);
      target.closest = () => null;
      documentEvents.click({target});
    },
    elapsed() { return node('tripElapsed').textContent; }};
}
const storage = {};
let app = boot(storage);
assert.equal(app.elapsed(), '00:00:00');
assert.equal(app.node('tripArrive').disabled, true);
app.click('tripArrive'); assert.equal(storage[key], undefined);
app.click('tripDepart');
assert.equal(app.node('tripTimer').dataset.state, 'running');
assert.equal(app.node('tripDepartLabel').textContent, '출발 시각');
assert.equal(app.node('tripDepartTime').textContent, '23:59:50');
assert.equal(app.node('tripDepart').disabled, true);
app.at(base + 1500); app.click('tripDepart');
assert.equal(JSON.parse(storage[key]).startedAt, base, 'Repeated departure must not reset the running trip');

// No interval callback is needed while a screen is off. One update catches up.
app.doc.hidden = true; app.at(base + 126000);
assert.equal(app.elapsed(), '00:00:01');
app.doc.hidden = false; app.documentEvents.visibilitychange();
assert.equal(app.elapsed(), '00:02:06');
assert.match(app.node('tripDepartTime').textContent, /^11\/10 23:59:50$/);

// Reloading or returning from another page restores the same departure.
app = boot(storage, base + 600000);
assert.equal(app.elapsed(), '00:10:00');
app.at(base + 3601234); app.click('tripArrive');
assert.equal(app.elapsed(), '01:00:01');
assert.equal(app.node('tripTimer').dataset.state, 'arrived');
assert.equal(app.node('tripArrive').disabled, true);
const stopped = storage[key];
assert.deepEqual(JSON.parse(stopped).history, [{startedAt:base, arrivedAt:base + 3601234}]);
app.at(base + 7200000); app.click('tripArrive');
assert.equal(app.elapsed(), '01:00:01'); assert.equal(storage[key], stopped);
app = boot(storage, base + 8000000);
assert.equal(app.elapsed(), '01:00:01');
assert.equal(app.node('tripDepart').textContent, '새 출발');
app.click('tripDepart');
assert.equal(app.elapsed(), '00:00:00');
assert.equal(JSON.parse(storage[key]).arrivedAt, null);
assert.deepEqual(JSON.parse(storage[key]).history, JSON.parse(stopped).history);
app.at(base + 8060000); app.click('tripArrive');
assert.deepEqual(JSON.parse(storage[key]).history, [
  {startedAt:base + 8000000, arrivedAt:base + 8060000},
  {startedAt:base, arrivedAt:base + 3601234}
]);

// A previously completed timer belongs in the history after a new departure.
const legacy = {[key]:JSON.stringify({version:1, startedAt:base, arrivedAt:base + 25000})};
const migrated = boot(legacy, base + 40000);
migrated.click('tripDepart');
assert.deepEqual(JSON.parse(legacy[key]).history, [{startedAt:base, arrivedAt:base + 25000}]);

// A second tab and back-forward restoration show the latest persisted state.
storage[key] = JSON.stringify({version:1, startedAt:base, arrivedAt:base + 25000});
app.windowEvents.storage({key}); assert.equal(app.elapsed(), '00:00:25');
storage[key] = JSON.stringify({version:1, startedAt:base, arrivedAt:null});
app.windowEvents.pageshow(); assert.equal(app.node('tripTimer').dataset.state, 'running');
delete storage[key]; app.windowEvents.storage({key:null});
assert.equal(app.node('tripTimer').dataset.state, 'idle');

// Bad stored data must never break timetable startup or render NaN.
for (const raw of ['{', 'null', '{}', '{"version":1,"startedAt":"bad","arrivedAt":null}',
  JSON.stringify({version:1, startedAt:base, arrivedAt:base - 1})]) {
  const bad = boot({[key]:raw}); assert.equal(bad.elapsed(), '00:00:00');
}
const privateApp = boot({}, base, true);
assert.equal(privateApp.node('tripStorageNote').hidden, false);
privateApp.click('tripDepart'); privateApp.at(base + 61000);
privateApp.documentEvents.visibilitychange();
assert.equal(privateApp.elapsed(), '00:01:01', 'Storage denial still permits an in-page timer');
privateApp.click('tripArrive'); assert.equal(privateApp.node('tripTimer').dataset.state, 'arrived');

const longTrip = boot({[key]:JSON.stringify({version:1, startedAt:base, arrivedAt:null})}, base + 25*3600000);
assert.equal(longTrip.elapsed(), '25:00:00', 'An overnight trip must not wrap at 24 hours');
longTrip.at(base - 5000); assert.equal(longTrip.elapsed(), '00:00:00', 'A clock correction never produces negative time');
assert.match(html, /td\.appendChild\(departureSlot\(x, state\.day/);
assert.match(html, /e\.appendChild\(departureSlot\(r\.ext, state\.day/);

// The appointment and an earlier completed trip share one persistent document.
const earlier = {startedAt:base - 3600000, arrivedAt:base - 300000};
const upcoming = {[key]:JSON.stringify({version:1,...earlier})};
const slot = Date.parse('2026-11-11T00:20:00Z');
let scheduled = boot(upcoming, slot - 20000);
scheduled.reserve('9:20');
assert.equal(scheduled.node('tripStatus').textContent, '출발 예약');
assert.equal(scheduled.node('tripDepartLabel').textContent, '예약 출발');
assert.equal(scheduled.node('tripDepartTime').textContent, '09:20:00');
assert.equal(scheduled.elapsed(), '00:00:00');
assert.equal(scheduled.node('tripCountdown').hidden, false);
assert.equal(scheduled.node('tripRemaining').textContent, '00:00:20');
assert.equal(JSON.parse(upcoming[key]).startedAt, slot);
assert.deepEqual(JSON.parse(upcoming[key]).history, [earlier]);
assert.equal(scheduled.watches.size, 1);
scheduled.click('tripDepart');
assert.equal(JSON.parse(upcoming[key]).arrivedAt, earlier.arrivedAt);
assert.equal(scheduled.watches.size, 0);
scheduled.reserve('9:20');
scheduled = boot(upcoming, slot + 3500);
assert.equal(scheduled.node('tripStatus').textContent, '운행 중');
assert.equal(scheduled.node('tripDepartLabel').textContent, '예약 출발');
assert.equal(scheduled.node('tripDepartTime').textContent, '09:20:00');
assert.equal(scheduled.node('tripCountdown').hidden, true);
assert.equal(scheduled.elapsed(), '00:00:03');
assert.equal(JSON.parse(upcoming[key]).startedAt, slot);
scheduled.fix(37.247333, 127.078440);
assert.equal(JSON.parse(upcoming[key]).arrivedAt, null, 'No finish while still at the origin');
scheduled.at(slot + 7000);
scheduled.fix(37.254, 127.081, 200);
assert.equal(JSON.parse(upcoming[key]).leftArea, undefined, 'Reject an inaccurate departure fix');
scheduled.fix(37.254, 127.081, 10, slot - 1000);
assert.equal(JSON.parse(upcoming[key]).leftArea, undefined, 'Reject a fix before departure');
scheduled.fix(37.254, 127.081);
assert.equal(JSON.parse(upcoming[key]).leftArea, true);

scheduled = boot(upcoming, slot + 901000);
scheduled.fix(37.2475935, 127.0757373, 10, slot + 900000);
assert.equal(JSON.parse(upcoming[key]).arrivedAt, null, 'Seocheon intersection does not finish a trip');
scheduled.fix(37.2476648, 127.0791747, 101);
assert.equal(JSON.parse(upcoming[key]).arrivedAt, null, 'Reject an inaccurate arrival fix');
scheduled.fix(37.2476648, 127.0791747, 10, slot + 900500);
assert.equal(JSON.parse(upcoming[key]).arrivalPlace, '경희대 사거리');
assert.equal(JSON.parse(upcoming[key]).arrivedAt, slot + 900500, 'Use the GPS fix timestamp');
assert.equal(scheduled.watches.size, 1, 'Keep GPS active after recording the intersection');
assert.equal(scheduled.elapsed(), '00:15:00');
assert.equal(scheduled.node('tripDepartLabel').textContent, '예약 출발');
assert.equal(scheduled.node('tripDepartTime').textContent, '09:20:00');
assert.deepEqual(JSON.parse(upcoming[key]).history, [{startedAt:slot, arrivedAt:slot + 900500}, earlier]);
scheduled.at(slot + 980000);
assert.equal(scheduled.elapsed(), '00:15:00');
scheduled.at(slot + 1201000);
assert.equal(scheduled.watches.size, 0, 'Stop tracking after the gate announcement window');

const reopened = boot({}, slot - 10000);
reopened.reserve('9:20');
reopened.doc.hidden = true;
reopened.documentEvents.visibilitychange();
assert.equal(reopened.watches.size, 0);
reopened.at(slot + 14000);
reopened.doc.hidden = false;
reopened.documentEvents.visibilitychange();
assert.equal(reopened.elapsed(), '00:00:14');
reopened.denied();
assert.equal(reopened.watches.size, 0);
assert.equal(reopened.node('tripGpsRetry').hidden, false);
reopened.click('tripGpsRetry');
assert.equal(reopened.watches.size, 1);
reopened.click('tripArrive');
assert.equal(reopened.node('tripTimer').dataset.state, 'arrived');
assert.equal(reopened.watches.size, 0);

const friday = Date.parse('2026-11-13T00:25:00Z');
const future = {};
const fridayApp = boot(future, friday, false, ['2026-11-16']);
fridayApp.reserve('9:20');
assert.equal(JSON.parse(future[key]).startedAt, Date.parse('2026-11-17T00:20:00Z'));
fridayApp.reserve('9:20','saturday');
assert.equal(JSON.parse(future[key]).startedAt, Date.parse('2026-11-14T00:20:00Z'));
fridayApp.reserve('9:20','sunday');
assert.equal(JSON.parse(future[key]).startedAt, Date.parse('2026-11-15T00:20:00Z'));
const gate = boot({}, slot - 10000);
gate.reserve('9:20');
gate.at(slot + 1000);
gate.fix(37.254, 127.081);
gate.at(slot + 600000);
gate.fix(37.247333, 127.078440);
assert.equal(gate.node('tripLocationStatus').textContent, '자동 도착 · 경희대 정문');

const manualData = {};
const manual = boot(manualData, slot - 10000);
manual.click('tripDepart');
assert.equal(manual.watches.size, 1, 'Manual start must use the same GPS detection as a reservation');
manual.fix(37.2474500, 127.0778667);
assert.equal(JSON.parse(manualData[key]).arrivedAt, null, 'Stay running while parked at the departure point');
manual.at(slot + 60000);
manual.fix(37.2504, 127.0793, 60);
assert.equal(JSON.parse(manualData[key]).leftArea, true, 'Moderate GPS error still permits departure');
manual.at(slot + 720000);
assert.ok(manual.probes.length > 0, 'Watch silence requests a fresh GPS fix');
manual.probes.at(-1).success({
  coords:{latitude:37.2474500,longitude:127.0778667,accuracy:80},
  timestamp:slot+720000
});
assert.equal(JSON.parse(manualData[key]).arrivalPlace, '경희대 정문');
assert.equal(manual.watches.size, 0);
manual.probes[0].success({
  coords:{latitude:37.2476648,longitude:127.0791747,accuracy:10},
  timestamp:slot+720000
});
assert.equal(JSON.parse(manualData[key]).arrivalPlace, '경희대 정문', 'Late GPS requests cannot change a completed trip');

const legacyRun = boot({[key]:JSON.stringify({version:1,startedAt:slot,arrivedAt:null})}, slot+10000);
assert.equal(legacyRun.watches.size, 1, 'Restore GPS for existing manually started trips');

const editingTime = slot + 10 * 60000;
const corrected = {[key]:JSON.stringify({version:1,...earlier})};
let editing = boot(corrected, editingTime);
const oldSlot = editing.slot('9:30');
const correctedSlot = editing.slot('9:20');
editing.click('tripDepart');
editing.fix(37.254, 127.081);
assert.equal(oldSlot.attrs['aria-pressed'], 'true');
editing.reserve('9:20');
assert.equal(editing.node('tripTimer').dataset.state, 'running');
assert.equal(editing.node('tripDepartLabel').textContent, '예약 출발');
assert.equal(editing.node('tripDepartTime').textContent, '09:20:00');
assert.equal(editing.elapsed(), '00:10:00');
assert.equal(oldSlot.attrs['aria-pressed'], 'false');
assert.equal(correctedSlot.attrs['aria-pressed'], 'true');
assert.equal(JSON.parse(corrected[key]).leftArea, true, 'A time correction keeps GPS arrival armed');
editing = boot(corrected, editingTime + 60000);
assert.equal(editing.slot('9:20').attrs['aria-pressed'], 'true', 'Restore the selected time after reload');
editing.fix(37.247333, 127.078440);
assert.equal(editing.node('tripLocationStatus').textContent, '자동 도착 · 경희대 정문');
assert.deepEqual(JSON.parse(corrected[key]).history, [{startedAt:slot, arrivedAt:editingTime + 60000}, earlier]);

const previousDay = {[key]:JSON.stringify({
  version:1, startedAt:slot - 86400000, arrivedAt:null, autoArrival:true, leftArea:true, history:[earlier]
})};
const replacing = boot(previousDay, editingTime);
replacing.reserve('9:20');
assert.equal(JSON.parse(previousDay[key]).startedAt, slot);
assert.equal(JSON.parse(previousDay[key]).leftArea, undefined, 'A stale trip must leave the origin again');
replacing.fix(37.247333, 127.078440);
assert.equal(replacing.node('tripTimer').dataset.state, 'running');
const futureSlot = replacing.slot('9:35');
replacing.reserve('9:35');
assert.equal(replacing.node('tripTimer').dataset.state, 'scheduled');
assert.equal(replacing.node('tripDepartTime').textContent, '09:35:00');
assert.equal(replacing.elapsed(), '00:00:00');
assert.equal(replacing.node('tripRemaining').textContent, '00:05:00');
assert.equal(futureSlot.attrs['aria-pressed'], 'true');
assert.deepEqual(JSON.parse(previousDay[key]).history, [earlier]);
replacing.at(slot + 15 * 60000);
assert.equal(replacing.node('tripTimer').dataset.state, 'running');

assert.match(html, /#tripTimer\[data-state="scheduled"\] #tripElapsed\{color:#82caff\}/);
assert.match(html, /#tripTimer\[data-state="running"\] #tripElapsed,\s*#tripTimer\[data-state="arrived"\] #tripElapsed\{color:#ffdf58\}/);
assert.doesNotMatch(html, /data-trip-phase/);
const colors = boot({}, slot-1000);
const selectedSlot = colors.slot('9:20');
colors.reserve('9:20');
assert.equal(colors.node('tripTimer').dataset.state, 'scheduled');
assert.equal(selectedSlot.attrs['aria-pressed'], 'true');
colors.at(slot);
assert.equal(colors.node('tripTimer').dataset.state, 'running');
assert.equal(selectedSlot.attrs['aria-pressed'], 'true');
colors.at(slot + 120000);
colors.click('tripArrive');
assert.equal(colors.node('tripTimer').dataset.state, 'arrived');
assert.equal(selectedSlot.attrs['aria-pressed'], 'false');

const notes = [];
const spoken = [];
const departureVoice = './audio/trip/departure-ko.mp3';
const gateVoice = './audio/trip/kyung-hee-gate-ko.mp3';
const worker = readFileSync(root + '/sw.js', 'utf8');
for (const path of [departureVoice, gateVoice]) {
  assert.ok(worker.includes(JSON.stringify(path)), 'Precache each voice in the service worker');
  assert.ok(readFileSync(root + '/' + path).length > 0, 'Deploy each speech clip');
}
const settleAudio = () => new Promise(resolve => setImmediate(resolve));
let audioResumes = 0;
class TestAudioContext {
  state = 'suspended';
  currentTime = 0;
  destination = {};
  async resume() { audioResumes++; this.state = 'running'; }
  async decodeAudioData(path) { return {path, duration:1.4}; }
  createBufferSource() {
    return {connect() {}, start(at) { spoken.push({path:this.buffer.path, at}); }};
  }
  createOscillator() {
    let frequency;
    return {
      frequency:{setValueAtTime(value) { frequency = value; }},
      connect() {},
      start(at) { if (frequency !== undefined) notes.push({frequency, at}); },
      stop() {}
    };
  }
  createGain() {
    return {gain:{setValueAtTime() {}, exponentialRampToValueAtTime() {}}, connect() {}, disconnect() {}};
  }
}
const chimeStorage = {};
const chime = boot(chimeStorage, slot - 1000, false, [], TestAudioContext);
const secondTab = boot(chimeStorage, slot - 1000, false, [], TestAudioContext);
secondTab.click('tripSoundCheck');
await settleAudio();
assert.deepEqual(spoken.map(voice => voice.path), [departureVoice, gateVoice]);
assert.ok(spoken[1].at >= spoken[0].at + 1.4, 'The two preview sentences play in order');
assert.equal(notes.length, 0, 'The preview uses the voice recordings');
assert.equal(chimeStorage[key], undefined);
secondTab.click('tripSoundCheck');
assert.equal(spoken.length, 2, 'Repeated preview taps do not layer announcements');
spoken.length = 0;
chime.reserve('9:20');
await settleAudio();
assert.equal(audioResumes, 2, 'The reservation tap enables audio for the later GPS callback');
assert.equal(spoken.length, 0, 'The reservation tap is quiet until departure');
secondTab.windowEvents.storage({key});
chime.at(slot + 1000);
secondTab.at(slot + 1000);
chime.fix(37.254, 127.081);
assert.deepEqual(spoken.map(voice => voice.path), [departureVoice], 'Speak once at the scheduled departure');
chime.at(slot + 120000);
chime.fix(37.2476648, 127.0791747);
assert.equal(notes.length, 9, 'The intersection still plays three chimes');
assert.equal(spoken.length, 1, 'Wait for the gate before speaking the arrival announcement');
for (const repeat of [0, 1, 2]) {
  const group = notes.slice(repeat * 3, 3 + repeat * 3);
  assert.deepEqual(group.map(note => note.frequency), [1318.51, 1046.50, 783.99]);
  assert.deepEqual(group.map(note => Math.round(note.at * 100)), [4, 31, 58].map(at => at + repeat * 145));
}
const recordedAt = JSON.parse(chimeStorage[key]).arrivedAt;
chime.at(slot + 130000);
chime.fix(37.247333, 127.078440);
assert.deepEqual(spoken.map(voice => voice.path), [departureVoice, gateVoice], 'Speak on reaching the gate after the intersection');
assert.equal(JSON.parse(chimeStorage[key]).arrivedAt, recordedAt, 'Gate speech leaves the recorded arrival time intact');
assert.equal(chime.watches.size, 0, 'Stop watching after the gate announcement');
chime.at(slot + 135000);
chime.fix(37.247333, 127.078440);
chime.click('tripArrive');
chime.windowEvents.pageshow();
secondTab.windowEvents.storage({key});
assert.equal(notes.length, 9, 'Repeated taps and restoring arrival do not replay the chime');
assert.equal(spoken.length, 2, 'Repeated GPS fixes and restores do not replay the gate voice');
const manualChime = boot({}, slot, false, [], TestAudioContext);
manualChime.click('tripDepart');
await settleAudio();
assert.equal(audioResumes, 3, 'The manual departure tap also enables audio');
assert.equal(spoken.at(-1).path, departureVoice, 'Manual departure also speaks');
manualChime.reserve('9:19');
assert.equal(spoken.length, 3, 'Correcting a past departure does not replay the departure voice');
manualChime.at(slot + 1000);
manualChime.click('tripArrive');
assert.equal(notes.length, 18, 'Manual arrival plays the same chime');

notes.length = 0;
spoken.length = 0;
let audioBlocked = true;
class InterruptedAudioContext extends TestAudioContext {
  async resume() {
    if (audioBlocked) throw Error('Playback blocked');
    await super.resume();
  }
}
const blockedChime = boot({}, slot, false, [], InterruptedAudioContext);
blockedChime.click('tripDepart');
await settleAudio();
assert.equal(spoken.length, 0);
assert.match(blockedChime.node('tripSoundStatus').textContent, /운행음 대기 중/);
audioBlocked = false;
blockedChime.click('tripSoundCheck');
assert.deepEqual(spoken.map(voice => voice.path), [departureVoice], 'A new tap plays only the pending departure');
assert.equal(blockedChime.node('tripSoundStatus').hidden, true);

spoken.length = 0;
const restoredChime = boot({[key]:JSON.stringify({version:1, startedAt:slot, arrivedAt:null, autoArrival:true, leftArea:true})}, slot + 120000, false, [], TestAudioContext);
restoredChime.fix(37.247333, 127.078440);
assert.equal(restoredChime.node('tripTimer').dataset.state, 'arrived');
assert.match(restoredChime.node('tripSoundStatus').textContent, /운행음 대기 중/);
restoredChime.click('tripSoundCheck');
await settleAudio();
assert.deepEqual(spoken.map(voice => voice.path), [gateVoice], 'A tap recovers the direct GPS gate announcement after a reload');

spoken.length = 0;
const missedDepartureStorage = {};
const missedDeparture = boot(missedDepartureStorage, slot - 1000, false, [], TestAudioContext);
missedDeparture.reserve('9:20');
missedDeparture.doc.hidden = true;
missedDeparture.at(slot + 120000);
missedDeparture.doc.hidden = false;
missedDeparture.documentEvents.visibilitychange();
assert.equal(missedDeparture.node('tripTimer').dataset.state, 'running');
await settleAudio();
assert.equal(spoken.length, 0, 'Do not replay a stale departure on return to the page');

console.log('Trip timer: Korean speech for departure and main gate, and three chimes for manual or intersection arrival');
console.log('Trip timer: one-tap correction while running, persistent selection, replacement reservation, GPS and recording');
console.log('Rev195: manual and restored trips use GPS, stationary GPS fallback, and moderate location error passed');
console.log('Rev195: time selection, scheduled start, holiday rollover, GPS departure and return, both destinations, permission retry, and manual arrival passed');
console.log('Rev189: trip start/arrival, sleep and reload recovery, midnight, fixed result, new trip, repeated taps, cross-tab restoration and unavailable/corrupt storage passed');
