import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const root=process.argv[2]||'_site', html=readFileSync(root+'/index.html','utf8');
const code=html.match(/<script id="rev172-outdoor-script">([\s\S]*?)<\/script>/)[1];
assert.ok(html.indexOf('id="kmaInitialSnapshot"')<html.indexOf('id="rev172-outdoor-script"'));
assert.doesNotMatch(code,/open-meteo|displayOffsetC|timeout:20000|abort\(\),12000\)|setTimeout\(load,800/);
let now=Date.parse('2026-10-28T21:40:00+09:00');
class Clock extends Date {constructor(...a){super(...(a.length?a:[now]));}static now(){return now;}}
const flush=async()=>{for(let i=0;i<15;i++)await Promise.resolve();};
function fixture({embedded=true,delayedGps=false,delayedNetwork=false,denied=false,stale=false,coarse=false}={}) {
  const nodes=new Map(),requests=[],positions=[],events={},intervals=[];let resolveNetwork;
  const node=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'',innerHTML:'',setAttribute(k,v){this[k]=v;}});return nodes.get(id);};
  const data={schema:1,source:'기상청 날씨누리',fetchedAt:now-(stale?46*60000:0),stations:[
    {id:'550',name:'오산',latitude:37.1693,longitude:127.05271,temperature:4.1,observedAt:now-10*60000}],
    conditions:[{name:'수원',latitude:37.25746,longitude:126.983,description:'맑음',observedAt:now-40*60000}]};
  if(embedded)node('kmaInitialSnapshot').textContent=JSON.stringify(data);
  const position={coords:{latitude:37.21,longitude:127.06,accuracy:15},timestamp:now};
  vm.runInNewContext(code,{Date:Clock,Intl,Math,Number,Promise,AbortController,
    setTimeout(){return 1;},setInterval(fn,ms){intervals.push([fn,ms]);},clearTimeout(){},
    navigator:{geolocation:{getCurrentPosition(ok,err,opts){positions.push({ok,err,opts});if(denied)err({code:1});else if(coarse&&positions.length===1)ok({...position,coords:{...position.coords,accuracy:12000}});else if(!delayedGps)ok({...position,timestamp:now});}}},
    document:{hidden:false,getElementById:node,addEventListener(k,fn){events[k]=fn;}},
    window:{addEventListener(k,fn){events[k]=fn;}},
    fetch(url){requests.push(url);return delayedNetwork?new Promise(r=>{resolveNetwork=()=>r({ok:true,json:async()=>data});}):Promise.resolve({ok:true,json:async()=>data});}});
  return {node,requests,positions,events,data,position,intervals,resolveNetwork:()=>resolveNetwork?.()};
}
// A slow refresh request cannot hold up the first reading from embedded data.
const fast=fixture({delayedGps:true,delayedNetwork:true});
assert.equal(fast.positions[0].opts.enableHighAccuracy,false);
assert.equal(fast.positions[0].opts.maximumAge,60000);
assert.equal(fast.positions[0].opts.timeout,2500);
assert.equal(fast.requests.length,0);
fast.positions[0].ok(fast.position);await flush();
assert.equal(fast.node('outdoorTempValue').textContent,'4.1°C');
assert.match(fast.node('outdoorWeatherIcon').innerHTML,/fff3a3/);
assert.equal(fast.requests.length,1,'Refresh starts after the temperature is already visible');
assert.ok(fast.requests.every(url=>url.startsWith('https://timetable-kma-feed.gusibzo.chatgpt.site/api/kma')&&!url.includes('latitude')));
// Without embedded data, both requests begin together, not GPS then fetch.
const parallel=fixture({embedded:false,delayedGps:true,delayedNetwork:true});
assert.equal(parallel.positions.length,1);assert.equal(parallel.requests.length,1);
parallel.resolveNetwork();parallel.positions[0].ok(parallel.position);await flush();
assert.equal(parallel.node('outdoorTempValue').textContent,'4.1°C');
const retry=fixture({coarse:true});await flush();
assert.equal(retry.positions.length,2);assert.equal(retry.positions[1].opts.enableHighAccuracy,true);assert.equal(retry.positions[1].opts.timeout,5000);
assert.equal(retry.node('outdoorTempValue').textContent,'4.1°C');
const noPermission=fixture({denied:true});await flush();assert.equal(noPermission.node('outdoorTempValue').textContent,'--°C');
const old=fixture({stale:true});await flush();assert.equal(old.node('outdoorTempValue').textContent,'--°C');assert.match(old.node('outdoorTempBtn')['aria-label'],/자동 갱신/);
const cadence=fixture();await flush();assert.equal(cadence.intervals[0][1],300000);
const before=cadence.requests.length;
now+=299999;await cadence.events.pageshow();await flush();assert.equal(cadence.requests.length,before);
now+=1;await cadence.intervals[0][0]();await flush();assert.equal(cadence.requests.length,before+1,'Refresh the KMA feed at five minutes');
console.log('Rev172 embedded startup avoids a blocking download; GPS/data requests run concurrently; short GPS fallback, stale data and denied permission passed');
