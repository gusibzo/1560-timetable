import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const root=process.argv[2]||'_site';
const page=readFileSync(root+'/cctv.html','utf8');
const main=readFileSync(root+'/index.html','utf8');
const data=page.match(/<script id="cctvCameraData" type="application\/json">([\s\S]*?)<\/script>/)[1];
const cameras=JSON.parse(data).filter(camera=>(camera.group||17)===17);
const code=page.match(/<script id="rev160-cctv-controller">([\s\S]*?)<\/script>/)[1];
for(const channel of [6043,100,78]) assert.ok(main.includes('./cctv.html?channel='+channel));
assert.ok(readFileSync(root+'/sw.js','utf8').includes('"./cctv.html"'));

function fixture(channel=6043){
  const nodes=new Map(),loads=[];
  const node=id=>{
    if(!nodes.has(id)){
      const el={textContent:'',value:'',disabled:false,events:{},children:[],
        addEventListener(name,fn){this.events[name]=fn;},
        setAttribute(name,value){this[name]=value;},
        appendChild(child){this.children.push(child);}};
      if(id==='cctvFrame')Object.defineProperty(el,'src',{set(value){loads.push(value);},get(){return loads.at(-1);}});
      nodes.set(id,el);
    }
    return nodes.get(id);
  };
  node('cctvCameraData').textContent=data;
  const location={href:'https://gusibzo.github.io/1560-timetable/cctv.html?channel='+channel,search:'?channel='+channel};
  vm.runInNewContext(code,{URL,URLSearchParams,location,history:{replaceState(a,b,url){location.href=url;location.search=new URL(url).search;}},document:{getElementById:node,createElement:()=>({})}});
  return{node,loads,location,click(id){node(id).events.click();},choose(channel){node('cameraSelect').value=String(channel);node('cameraSelect').events.change();},channel(){return Number(new URL(loads.at(-1)).searchParams.get('channel'));}};
}
const f=fixture();
assert.equal(f.channel(),6043);
assert.equal(f.node('nextName').textContent,'서초IC');
assert.equal(f.node('previousName').textContent,'잠원IC');
f.click('cctvNext');
assert.equal(f.channel(),6044,'Next must load the actual next camera document');
assert.match(f.node('cameraTitle').textContent,/서초IC/);
f.click('cctvPrevious');assert.equal(f.channel(),6043);
f.click('cctvPrevious');assert.equal(f.channel(),955);
assert.match(f.node('cameraTitle').textContent,/잠원IC/);
for(const channel of [100,78]){
  f.choose(channel);assert.equal(f.channel(),channel);
  assert.equal(Number(new URL(f.location.href).searchParams.get('channel')),channel);
  assert.equal(f.node('cctvSource').href,f.loads.at(-1));
}
let count=f.loads.length;f.click('cctvReload');assert.equal(f.loads.length,count+1);
f.choose(cameras[0].channel);assert.equal(f.node('cctvPrevious').disabled,true);
count=f.loads.length;f.click('cctvPrevious');assert.equal(f.loads.length,count);
f.choose(cameras.at(-1).channel);assert.equal(f.node('cctvNext').disabled,true);
count=f.loads.length;f.click('cctvNext');assert.equal(f.loads.length,count);
const invalid=fixture('https://example.com');assert.equal(invalid.channel(),6043);
assert.ok(f.loads.every(url=>new URL(url).origin==='https://rtt.map.naver.com'));
assert.equal(f.node('cameraSelect').children.length,cameras.length);
// A CCTV navigation must never overwrite the cached timetable.
const handlers={}, saved=new Map();
const indexUrl='https://gusibzo.github.io/1560-timetable/index.html';
const viewerUrl='https://gusibzo.github.io/1560-timetable/cctv.html';
saved.set(indexUrl,new Response('timetable'));
let offline=false;
vm.runInNewContext(readFileSync(root+'/sw.js','utf8'),{
  URL,Request,Response,Headers,
  self:{location:{origin:'https://gusibzo.github.io'},registration:{scope:'https://gusibzo.github.io/1560-timetable/'},addEventListener(name,fn){handlers[name]=fn;}},
  caches:{async open(){return {async put(key,value){saved.set(String(key.url||key),value);},async match(key){return saved.get(String(key.url||key))?.clone();}};}},
  async fetch(){if(offline)throw Error('offline');return new Response('CCTV viewer');}
});
async function navigate(channel){let result;handlers.fetch({request:{method:'GET',mode:'navigate',url:viewerUrl+'?channel='+channel},respondWith(value){result=value;}});return await result;}
assert.equal(await (await navigate(6043)).text(),'CCTV viewer');
assert.equal(await saved.get(indexUrl).clone().text(),'timetable');
assert.ok(saved.has(viewerUrl));
offline=true;
assert.equal(await (await navigate(100)).text(),'CCTV viewer','The viewer cache works across camera query strings');
console.log('Rev160 CCTV entry links, next/previous camera loads, selection, reload, bounds and allowed origins passed');
