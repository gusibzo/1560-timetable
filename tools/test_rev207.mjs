import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";

const root = process.argv[2] || "_site";
const read = path => readFileSync(`${root}/${path}`, "utf8");
const timetable = read("index.html");
const guide = read("route-video.html");
assert.doesNotMatch(guide, /intent:\/\/|href="[^"]*\.apk/);
const scrollScript = read("android-route-video/assets/route-scroll.js");

for (const route of ["A", "B"]) {
  assert.match(timetable, new RegExp(`href="\\./route-video\\.html\\?start=1#record-${route}" data-route-video="${route}">● 1560${route} 노선 녹화`));
  assert.ok(guide.includes('href="#record-' + route + '"'));
  const dataset = JSON.parse(read("route-video-data/" + route + ".json"));
  assert.equal(dataset.route, route);
  assert.ok(dataset.stops.length > 2);
  assert.ok(dataset.stops.every((station, i) => station.name && (!i || station.seq > dataset.stops[i-1].seq)));

  const list = {
    clientHeight: 500, scrollHeight: 850, scrollTop: 125, isConnected: true,
    scrollTo({top}) { this.scrollTop = top; }
  };
  const window = {};
  let frame;
  runInNewContext(scrollScript, {
    window,
    document: {body: {innerText: `1560${route}번\n정류장`}, querySelector: () => ({parentElement: list})},
    getComputedStyle: () => ({overflowY: "auto"}),
    performance: {now: () => 0},
    requestAnimationFrame(callback) { frame = callback; },
    cancelAnimationFrame() { frame = undefined; }
  });
  const scrolling = window.routeVideo1560;
  const otherRoute = route === "A" ? "B" : "A";
  assert.equal(scrolling.ready(otherRoute), false);
  assert.equal(scrolling.start(otherRoute), false);
  assert.equal(scrolling.ready(route), true);
  assert.equal(scrolling.rewind(route), true);
  assert.equal(list.scrollTop, 0);
  assert.equal(scrolling.start(route), true);
  for (let time = 50; frame && time <= 10_000; time += 50) {
    const tick = frame;
    frame = undefined;
    tick(time);
  }
  assert.equal(scrolling.state(), "done");
  assert.equal(list.scrollTop, 350);
}
console.log("1560A and 1560B recording links and automatic scrolling passed");
