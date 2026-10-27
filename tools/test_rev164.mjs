import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const html=readFileSync((process.argv[2]||'_site')+'/index.html','utf8');
const script=html.match(/<script id="rev144-outdoor-script">([\s\S]*?)<\/script>/)[1];
function fixture(){
  const nodes=new Map(),events={},requests=[],positionOptions=[];
  const f={now:Date.parse('2026-10-28T06:14:00+09:00'),lat:37.5,lon:127,accuracy:25,positionAge:0,weatherAge:0,temp:-1,unit:'°C',denied:false};
  class Clock extends Date {constructor(...args){super(...(args.length?args:[f.now]));}static now(){return f.now;}}
  const node=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'',innerHTML:'',hidden:true,open:false,
    showModal(){this.open=true;},setAttribute(key,value){this[key]=value;},addEventListener(key,fn){events[id+':'+key]=fn;}});return nodes.get(id);};
  let initial;
  vm.runInNewContext(script,{
    URLSearchParams,AbortController,Intl,Date:Clock,
    document:{hidden:false,getElementById:node,addEventListener(name,fn){events[name]=fn;}},
    window:{addEventListener(name,fn){events[name]=fn;}},
    navigator:{geolocation:{getCurrentPosition(ok,err,opts){positionOptions.push(opts);if(f.denied)return err({code:1});ok({timestamp:f.now-f.positionAge,coords:{latitude:f.lat,longitude:f.lon,accuracy:f.accuracy}});}}},
    setTimeout(fn,delay){if(delay===800)initial=fn;return 1;},clearTimeout(){},setInterval(){},
    async fetch(url){requests.push(new URL(url));return{ok:true,async json(){return{timezone:'Asia/Seoul',current_units:{temperature_2m:f.unit},current:{temperature_2m:f.temp,weather_code:0,is_day:0,time:(f.now-f.weatherAge)/1000}};}};}
  });
  return Object.assign(f,{node,requests,positionOptions,open:()=>initial(),refresh:()=>events['outdoorTempRefresh:click'](),poll:()=>events.pageshow(),click:()=>events['outdoorTempBtn:click']()});
}
const f=fixture();await f.open();
assert.equal(f.node('outdoorTempValue').textContent,'-1°C','A negative estimate is preserved, never corrected with an arbitrary offset');
assert.equal(f.positionOptions[0].enableHighAccuracy,true);
assert.equal(f.positionOptions[0].maximumAge,0);
assert.match(f.node('outdoorTempBasis').textContent,/추정 · 06:14/);
assert.match(f.node('outdoorTempUpdate').textContent,/위치 오차 약 25m/);
await f.poll();assert.equal(f.requests.length,1);
f.accuracy=5000;await f.poll();
assert.equal(f.requests.length,1,'Do not fetch or reuse cached weather for imprecise location');
assert.equal(f.node('outdoorTempValue').textContent,'위치 확인');
assert.equal(f.node('outdoorWeatherIcon').hidden,true);
assert.equal(f.node('outdoorTempBasis').textContent,'');
f.accuracy=25;f.positionAge=120000;await f.refresh();
assert.equal(f.node('outdoorTempValue').textContent,'위치 확인');
f.positionAge=0;await f.refresh();
f.lat+=0.006;f.temp=4;let count=f.requests.length;await f.poll();
assert.equal(f.requests.length,count+1,'Movement beyond 500m refreshes even within two minutes');
assert.equal(f.node('outdoorTempValue').textContent,'4°C');
f.now+=121000;f.temp=5;count=f.requests.length;await f.poll();
assert.equal(f.requests.length,count+1,'Stationary weather cache expires after two minutes');
f.weatherAge=3600000;await f.refresh();assert.equal(f.node('outdoorTempValue').textContent,'다시 시도');
f.weatherAge=-600000;await f.refresh();assert.equal(f.node('outdoorTempValue').textContent,'다시 시도');
f.weatherAge=0;f.unit='°F';await f.refresh();assert.equal(f.node('outdoorTempValue').textContent,'다시 시도');
f.unit='°C';f.denied=true;await f.refresh();assert.equal(f.node('outdoorTempValue').textContent,'위치 허용');
f.denied=false;await f.refresh();count=f.requests.length;
f.click();await new Promise(resolve=>setImmediate(resolve));
assert.equal(f.node('outdoorTempDialog').open,true);
assert.equal(f.requests.length,count+1,'Tapping the temperature explicitly refreshes both position and weather');
console.log('Rev164 high-accuracy fresh location, uncertainty rejection, movement/cache expiry, timestamps, manual refresh and weather validation passed');
