import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const html = readFileSync((process.argv[2] || '_site') + '/index.html', 'utf8');
const code = html.match(/<script id="rev189-trip-timer">([\s\S]*?)<\/script>/)[1];
assert.equal((html.match(/id="tripTimer"/g) || []).length, 1);
assert.ok(html.indexOf('id="tripTimer"') > html.indexOf('id="roadTrafficBtn"'));
assert.ok(html.indexOf('id="tripTimer"') < html.indexOf('<nav class="switch"'));
const key = 'bus1560-trip-timer-v1';
const base = Date.parse('2026-11-10T14:59:50Z'); // 23:59:50 in Korea.
function boot(storage, initial = base, blocked = false) {
  const nodes = new Map(), windowEvents = {}, documentEvents = {};
  let now = initial, interval;
  const node = id => {
    if (!nodes.has(id)) nodes.set(id, {textContent:'', dataset:{}, attrs:{}, events:{},
      addEventListener(name, cb) { this.events[name] = cb; },
      setAttribute(name, value) { this.attrs[name] = value; },
      removeAttribute(name) { delete this.attrs[name]; }});
    return nodes.get(id);
  };
  class Clock extends Date { static now() { return now; } }
  const doc = {hidden:false, getElementById:node, addEventListener(name, cb) { documentEvents[name] = cb; }};
  vm.runInNewContext(code, {Date:Clock, document:doc,
    window:{addEventListener(name, cb) { windowEvents[name] = cb; }},
    localStorage:{getItem(k) { if (blocked) throw Error('blocked'); return storage[k] ?? null; },
      setItem(k, value) { if (blocked) throw Error('blocked'); storage[k] = value; }},
    setInterval(cb) { interval = cb; }});
  return {node, doc, windowEvents, documentEvents,
    at(value) { now = value; interval(); },
    click(id) { node(id).events.click(); },
    elapsed() { return node('tripElapsed').textContent; }};
}
const storage = {};
let app = boot(storage);
assert.equal(app.elapsed(), '00:00:00');
assert.equal(app.node('tripArrive').disabled, true);
app.click('tripArrive'); assert.equal(storage[key], undefined);
app.click('tripDepart');
assert.equal(app.node('tripTimer').dataset.state, 'running');
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
app.at(base + 7200000); app.click('tripArrive');
assert.equal(app.elapsed(), '01:00:01'); assert.equal(storage[key], stopped);
app = boot(storage, base + 8000000);
assert.equal(app.elapsed(), '01:00:01');
assert.equal(app.node('tripDepart').textContent, '새 출발');
app.click('tripDepart');
assert.equal(app.elapsed(), '00:00:00');
assert.equal(JSON.parse(storage[key]).arrivedAt, null);

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
console.log('Rev189: trip start/arrival, sleep and reload recovery, midnight, fixed result, new trip, repeated taps, cross-tab restoration and unavailable/corrupt storage passed');
