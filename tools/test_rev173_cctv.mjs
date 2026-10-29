import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const root=process.argv[2]||'_site';
const main=readFileSync(root+'/index.html','utf8');
const viewer=readFileSync(root+'/cctv.html','utf8');
const sw=readFileSync(root+'/sw.js','utf8');
assert.equal((viewer.match(/id="cctvLoading"/g)||[]).length,1,'The loading element must exist in the actual viewer');
assert.ok(main.includes('register("./sw.js?v=173"'));
assert.ok(viewer.includes("register('./sw.js?v=173'"));
assert.ok(!main.includes("url.searchParams.set('v', '169')"));
const registration=viewer.match(/<script id="rev162-viewer-update">([\s\S]*?)<\/script>/)[1];
for(const [search,expected] of [['?embedded=1',0],['?channel=6043',1]]){
  const registered=[];
  vm.runInNewContext(registration,{URLSearchParams,location:{search},navigator:{serviceWorker:{register(url){registered.push(url);return Promise.resolve({update(){}});}}}});
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(registered.length,expected,'An embedded camera must not install/update another worker');
}
const handlers={},deleted=[];let claimed=false;
vm.runInNewContext(sw,{URL,Request,Response,Headers,
  self:{addEventListener(k,fn){handlers[k]=fn;},clients:{claim(){claimed=true;},matchAll(){throw Error('Never navigate open camera or timetable windows on activation');}}},
  caches:{keys:async()=>['1560-timetable-rev172-v1','1560-timetable-rev173-v1'],delete:async name=>deleted.push(name)}});
let activation;handlers.activate({waitUntil(p){activation=p;}});await activation;
assert.equal(claimed,true);assert.deepEqual(deleted,['1560-timetable-rev172-v1']);
// Camera load completion must clear the delayed-connection notice.
const controller=viewer.match(/<script id="rev160-cctv-controller">([\s\S]*?)<\/script>/)[1];
const nodes=new Map(),timers=[];
const node=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'',events:{},children:[],addEventListener(k,fn){this.events[k]=fn;},appendChild(x){this.children.push(x);},setAttribute(k,v){this[k]=v;}});return nodes.get(id);};
node('cctvCameraData').textContent=viewer.match(/<script id="cctvCameraData" type="application\/json">([\s\S]*?)<\/script>/)[1];
vm.runInNewContext(controller,{URL,URLSearchParams,location:{href:'https://gusibzo.github.io/1560-timetable/cctv.html?channel=6043',search:'?channel=6043'},history:{replaceState(){}},document:{getElementById:node,createElement:()=>({})},setTimeout(fn,ms){timers.push([fn,ms]);return timers.length;},clearTimeout(){}});
assert.equal(node('cctvLoading').hidden,false);assert.equal(timers[0][1],12000);
timers[0][0]();assert.match(node('cctvLoading').textContent,/새로고침/);
node('cctvFrame').events.load();assert.equal(node('cctvLoading').hidden,true);
console.log('Rev173 CCTV: matching worker versions, no embedded updates or forced navigation, and bounded loading feedback passed');
