import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const root = process.argv[2] || '_site';
const html = readFileSync(root + '/index.html', 'utf8');
const script = html.match(/<script id="rev144-outdoor-script">([\s\S]*?)<\/script>/)?.[1];
assert.ok(script && html.includes('rev157-outdoor-weather'));
assert.equal((html.match(/id="outdoorWeatherIcon"/g)||[]).length,1);

function fixture() {
  const elements = new Map(), events = {}, requests = [];
  const el = id => {
    if(!elements.has(id)) elements.set(id,{textContent:'',innerHTML:'',hidden:true,
      setAttribute(name,value){this[name]=value;},
      addEventListener(name,fn){events[id+':'+name]=fn;}});
    return elements.get(id);
  };
  const f = {code:0,day:1,temp:12.3,age:0,deny:false,fail:false,requests,el};
  const document = {hidden:false,getElementById:el,addEventListener(name,fn){events[name]=fn;}};
  let initial;
  vm.runInNewContext(script,{
    document,window:{addEventListener(name,fn){events[name]=fn;}},
    navigator:{geolocation:{getCurrentPosition(ok,err){
      if(f.deny) err({code:1}); else ok({timestamp:Date.now(),coords:{latitude:37.5,longitude:127,accuracy:25}});
    }}},URLSearchParams,AbortController,Intl,Date,
    setTimeout(fn,delay){if(delay===800) initial=fn;return 1;},clearTimeout(){},setInterval(){},
    async fetch(url){requests.push(new URL(url));if(f.fail)throw Error('offline');return {
      ok:true,async json(){return {current:{temperature_2m:f.temp,weather_code:f.code,is_day:f.day,time:Math.floor(Date.now()/1000)-f.age},current_units:{temperature_2m:'°C'},timezone:'Asia/Seoul'};}
    };}
  });
  f.open=()=>initial();
  f.refresh=()=>events['outdoorTempRefresh:click']();
  f.returnToApp=()=>events.pageshow();
  return f;
}

const f=fixture();
await f.open();
assert.equal(f.requests[0].searchParams.get('current'),'temperature_2m,weather_code,is_day');
assert.equal(f.el('outdoorTempValue').textContent,'12°C');
assert.equal(f.el('outdoorWeatherIcon').hidden,false);
assert.match(f.el('outdoorWeatherIcon').innerHTML,/<circle cx="24"/,'Clear daylight shows the sun');
assert.match(f.el('outdoorTempBtn')['aria-label'],/맑음/);
f.day=0;await f.refresh();
assert.match(f.el('outdoorWeatherIcon').innerHTML,/M33 5/,'Clear night shows a moon');
assert.match(f.el('outdoorTempBtn')['aria-label'],/밤/);
for(const [code,label] of [[2,'구름 조금'],[3,'흐림'],[45,'안개'],[61,'비'],[73,'눈'],[95,'뇌우']]){
  f.code=code;await f.refresh();
  assert.equal(f.el('outdoorWeatherIcon').hidden,false);
  assert.match(f.el('outdoorTempMessage').textContent,new RegExp(label));
}
const previous=f.el('outdoorWeatherIcon').innerHTML, count=f.requests.length;
await f.returnToApp();
assert.equal(f.requests.length,count,'Nearby fresh readings reuse the cache');
assert.equal(f.el('outdoorWeatherIcon').innerHTML,previous,'Cached readings retain their matching icon');
f.code=undefined;await f.refresh();
assert.equal(f.el('outdoorTempValue').textContent,'12°C','Missing weather code does not discard valid temperature');
assert.equal(f.el('outdoorWeatherIcon').hidden,true,'Missing code must not invent clear skies');
f.code=0;f.day=undefined;await f.refresh();
assert.equal(f.el('outdoorWeatherIcon').hidden,true,'Unknown daylight must not invent a sun or moon');
f.day=1;f.temp=-12;await f.refresh();
assert.equal(f.el('outdoorTempValue').textContent,'-12°C');
f.fail=true;await f.refresh();
assert.equal(f.el('outdoorWeatherIcon').hidden,true,'Network failure clears the old weather icon');
assert.equal(f.el('outdoorTempValue').textContent,'다시 시도');
f.fail=false;f.age=7200;await f.refresh();
assert.equal(f.el('outdoorWeatherIcon').hidden,true,'Stale weather cannot show as current');
f.deny=true;await f.refresh();
assert.equal(f.el('outdoorTempValue').textContent,'위치 허용');
assert.equal(f.el('outdoorWeatherIcon').hidden,true);
console.log('Rev157 day/night, weather codes, cache, missing data and error-state checks passed');
