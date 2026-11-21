import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";

const root = process.argv[2] || "_site";
const read = path => readFileSync(`${root}/${path}`, "utf8");
const timetable = read("index.html");
const guide = read("route-video.html");
const launchScript = read("route-video-link.js");
const scrollScript = read("android-route-video/assets/route-scroll.js");

assert.match(guide, /href="\.\/downloads\/1560-route-video\.apk"/);
for (const route of ["A", "B"]) {
  assert.match(timetable, new RegExp(`href="\\./route-video\\.html#record-${route}" data-route-video="${route}">● 1560${route} 노선 녹화`));
  assert.match(guide, new RegExp(`id="record-${route}"[^>]*data-route-video="${route}"`));
  const link = {dataset: {routeVideo: route}, href: "#record-" + route, hidden: true};
  const document = {
    baseURI: "https://example.com/timetable/",
    querySelectorAll: () => [link]
  };
  runInNewContext(launchScript, {document, navigator: {userAgent: "Android"}, URL});
  const fallback = encodeURIComponent(`https://example.com/timetable/route-video.html#record-${route}`);
  assert.equal(link.href, `intent://record/${route}#Intent;scheme=routevideo1560ab;package=kr.palcheonjo.routevideo1560.ab;S.browser_fallback_url=${fallback};end`);
  assert.equal(link.hidden, false);

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
