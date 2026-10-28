import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const root=process.argv[2]||'_site';
const html=readFileSync(root+'/index.html','utf8');
const code=html.match(/<script id="rev170-outdoor-script">([\s\S]*?)<\/script>/)[1];
assert.doesNotMatch(code,/open-meteo|displayOffsetC|Math.round\(.*temperature/);
assert.match(html, /id="outdoorTempBtn" href="https:\/\/www.weather.go.kr\/w\/index.do"/);
let now=Date.parse('2026-10-28T20:25:00+09:00');
class Clock extends Date {constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}}
function fixture() {
  const nodes=new Map(),events={},timers=[],requests=[];
  const node=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'',innerHTML:'',setAttribute(k,v){this[k]=v;}});return nodes.get(id);};
  const f={coords:{latitude:37.21,longitude:127.06,accuracy:15}, denied:false, badNetwork:false,
    data:{schema:1,source:'기상청 날씨누리',fetchedAt:now,stations:[
      {id:'550',name:'오산',latitude:37.1693,longitude:127.05271,temperature:4.1,observedAt:now-15*60000},
      {id:'119',name:'수원',latitude:37.25746,longitude:126.983,temperature:6.5,observedAt:now-15*60000}],
      conditions:[{name:'수원',latitude:37.25746,longitude:126.983,description:'맑음',observedAt:now-25*60000}]},node,events,requests};
  vm.runInNewContext(code,{Date:Clock,Intl,Math,Number,Promise,AbortController,
    setTimeout(fn){timers.push(fn);return timers.length;},setInterval(){},clearTimeout(){},
    navigator:{geolocation:{getCurrentPosition(ok,err,opts){assert.equal(opts.enableHighAccuracy,true);f.denied?err({code:1}):ok({coords:f.coords,timestamp:now});}}},
    document:{hidden:false,getElementById:node,addEventListener(k,fn){events[k]=fn;}},window:{addEventListener(k,fn){events[k]=fn;}},
    async fetch(url){requests.push(url);if(f.badNetwork)throw Error('offline');return {ok:true,json:async()=>f.data};}});
  f.start=async()=>timers[0]();return f;
}
const f=fixture();await f.start();
assert.equal(f.node('outdoorTempValue').textContent,'4.1°C','Show the observed decimal, without a correction or integer rounding');
assert.match(f.node('outdoorTempBtn')['aria-label'],/오산 관측소.*20:10/);
assert.match(f.node('outdoorWeatherIcon').innerHTML, /fff3a3/,'Clear night uses the moon');
assert.ok(f.requests.every(url=>url.startsWith('./weather/kma.json?t=')&&!/latitude|longitude|37.21|127.06/.test(url)));
f.data.stations[0].temperature=0;await f.events.pageshow();assert.equal(f.node('outdoorTempValue').textContent,'0.0°C');
f.data.stations[0].temperature=-1.3;await f.events.pageshow();assert.equal(f.node('outdoorTempValue').textContent,'-1.3°C');
f.coords={latitude:37.25746,longitude:126.983,accuracy:15};await f.events.pageshow();assert.equal(f.node('outdoorTempValue').textContent,'6.5°C','Use the current location when the bus moves');
f.badNetwork=true;await f.events.pageshow();assert.equal(f.node('outdoorTempValue').textContent,'--°C','Do not retain an old reading on failure');
const stale=fixture();stale.data.stations.forEach(s=>s.observedAt=now-46*60000);await stale.start();assert.equal(stale.node('outdoorTempValue').textContent,'--°C');
const oldFile=fixture();oldFile.data.fetchedAt=now-46*60000;await oldFile.start();assert.equal(oldFile.node('outdoorTempValue').textContent,'--°C');
const denied=fixture();denied.denied=true;await denied.start();assert.equal(denied.requests.length,0);assert.equal(denied.node('outdoorTempValue').textContent,'--°C');
const malformed=fixture();malformed.data.stations.forEach(s=>s.temperature='');await malformed.start();assert.equal(malformed.node('outdoorTempValue').textContent,'--°C');
// Polling URLs must not accumulate snapshots in the service-worker cache.
const handlers={};let cacheReads=0,result;
vm.runInNewContext(readFileSync(root+'/sw.js','utf8'),{URL,Response,
  self:{location:{origin:'https://gusibzo.github.io'},registration:{scope:'https://gusibzo.github.io/1560-timetable/'},addEventListener(k,fn){handlers[k]=fn;}},
  caches:{async open(){cacheReads++;throw Error('Weather must bypass cache');}},
  async fetch(){return new Response('live weather');}});
handlers.fetch({request:{method:'GET',mode:'cors',url:'https://gusibzo.github.io/1560-timetable/weather/kma.json?t=1'},respondWith(r){result=r;}});
assert.equal(await (await result).text(),'live weather');assert.equal(cacheReads,0);
console.log('Rev170 KMA decimals, zero/negative temperatures, moving location, private GPS, moon, denial and stale/error handling passed');
