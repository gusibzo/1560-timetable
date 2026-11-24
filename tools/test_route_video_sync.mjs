// Deterministically check every scrolling frame without recording a video.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";

const script = readFileSync(new URL("../route-video.js", import.meta.url), "utf8");

async function checkRoute(route, clustered) {
  const routeData = JSON.parse(readFileSync(new URL(`../route-video-data/${route}.json`, import.meta.url), "utf8"));
  const {stops} = routeData;
  const values = [
    ["1234", 45, "#165532"], ["5678", 0, "#be2030"], ["6789", null, "#414c5a"], ["1004", 20, "#0066ff"],
    ["1005", 10, "#be2030"], ["1006", 21, "#165532"], ["1007", 11, "#ad226d"], ["1008", 44, "#165532"],
    ["1012", 12, "#ad226d"], ["1013", 13, "#0066ff"], ["3452", 18, "#0066ff"], ["6771", 19, "#0066ff"]
  ];
  const headingByVehicle = new Map(values.map(([vehicle, , color]) => [vehicle, color]));
  const indices = clustered ? [0, 0, 0, 1, 1, 40, 41, stops.length - 1, 12, 13, 18, 19] :
    values.map((_, i) => i);
  const buses = values.map(([vehicle, seats], i) => ({vehicle, seats, seq: stops[indices[i]].seq,
    stationId: stops[indices[i]].id})).reverse();
  const observation = {route, at: new Date().toISOString(), buses};
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {setAttribute() {}, removeAttribute() {}, addEventListener() {}});
    return elements.get(id);
  };
  let frame, matched = 0, empty = 0, callback, stopped = false;
  const seen = new Set();
  const count = `운행 ${buses.length}대`;
  const checkFrame = () => {
    if (!frame?.heading?.startsWith("운행 ")) return;
    const first = frame.vehicles[0];
    if (first) {
      assert.equal(frame.heading, `${count}  ·  ${first.number}호  ·  `);
      assert.equal(frame.seats, `잔여 ${first.seats}`);
      assert.equal(frame.color, headingByVehicle.get(first.number));
      seen.add(first.number);
      matched++;
    } else {
      assert.equal(frame.heading, count);
      assert.equal(frame.seats, undefined);
      empty++;
    }
  };
  const canvas = Object.assign(element("film"), {width: 720, height: 1140,
    getContext: () => ctx, captureStream: () => ({getTracks: () => []})});
  const ctx = {
    fillRect(x, y, w, h) {
      if (x === 0 && y === 0 && w === canvas.width && h === canvas.height) {
        checkFrame(); frame = {vehicles: []};
      }
    },
    fillText(text, x, y) {
      if (y === 256 && text.startsWith("운행 ")) frame.heading = text;
      if (y === 256 && text.startsWith("잔여 ")) {frame.seats = text; frame.color = this.fillStyle;}
      if (x === 86 && /^(\d+석|미제공)$/.test(text)) frame.badge = text;
      else if (x === 86 && frame.badge !== undefined) {
        const middle = y - 32;
        if (middle - 33 >= 372 && middle + 38 <= canvas.height) frame.vehicles.push({number: text, seats: frame.badge});
        delete frame.badge;
      }
    },
    measureText: text => ({width: text.length * 15}),
    beginPath() {}, roundRect() {}, fill() {}, arc() {}, stroke() {}, moveTo() {}, lineTo() {},
    save() {}, rect() {}, clip() {}, restore() {}
  };
  class Recorder {
    static isTypeSupported() { return true; }
    start() { this.state = "recording"; }
    stop() { this.state = "inactive"; stopped = true; }
  }
  const href = `https://example.invalid/route-video.html?start=1#record-${route}`;
  runInNewContext(script, {window: {MediaRecorder: Recorder, addEventListener() {}}, MediaRecorder: Recorder,
    document: {getElementById: element, querySelector: element, addEventListener() {}, hidden: false},
    location: new URL(href), history: {replaceState() {}}, URL, navigator: {}, AbortController,
    setTimeout: () => 0, clearTimeout() {}, setInterval() {}, performance: {now: () => 0},
    fetch: async url => ({ok: true, json: async () => url.includes("/api/gbis/") ? observation : routeData}),
    requestAnimationFrame: fn => {callback = fn; return 1;}, cancelAnimationFrame() {callback = undefined;}
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(typeof callback, "function");
  for (let now = 0; callback && now < 60_000; now += 25) {
    const tick = callback; callback = undefined; tick(now);
  }
  checkFrame();
  assert.ok(stopped, "Recording should finish at the last stop");
  assert.ok(matched > 10 && empty > 10, {matched, empty});
  // At the stop shared by the first three fixtures, reversing the feed puts the third vehicle first.
  assert.deepEqual([...seen].sort(), (clustered ? values.slice(2) : values).map(v => v[0]).sort());
  console.log(`1560${route} ${clustered ? "clustered" : "separate"}: ${matched} matched, ${empty} no visible vehicle frames`);
}

for (const route of ["A", "B"]) for (const clustered of [false, true]) await checkRoute(route, clustered);
