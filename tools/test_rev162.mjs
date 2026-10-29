import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const root=process.argv[2]||'_site';
const page=readFileSync(root+'/cctv.html','utf8');
const main=readFileSync(root+'/index.html','utf8');
const data=page.match(/<script id="cctvCameraData" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code=page.match(/<script id="rev160-cctv-controller">([\s\S]*?)<\/script>/)[1];
for(const channel of [6043,100,78]) assert.match(main,new RegExp(`\\./cctv\\.html\\?channel=${channel}&amp;v=(?:162|169|173)`));
assert.match(page, /id="cctvVideoHeading"/);
assert.match(page, /#cctvVideoHeading\{[^}]*inset:0 0 auto;[^}]*height:100px/);
assert.match(page, /#cctvClose\{width:100px;height:100px/);
const nodes=new Map(),replacements=[],appReplacements=[];
function node(id){
  if(!nodes.has(id))nodes.set(id,{textContent:'',events:{},value:'',children:[],
    addEventListener(name,fn){this.events[name]=fn;},setAttribute(name,value){this[name]=value;},appendChild(child){this.children.push(child);}});
  return nodes.get(id);
}
node('cctvFrame').contentWindow={location:{replace(url){replacements.push(url);}}};
Object.defineProperty(node('cctvFrame'),'src',{set(){throw Error('Do not push a new camera history entry when replace is available');}});
node('cctvCameraData').textContent=data;
const context={setTimeout(){return 1;},clearTimeout(){},URL,URLSearchParams,location:{href:'https://gusibzo.github.io/1560-timetable/cctv.html?channel=6043&v=162',search:'?channel=6043&v=162',replace(url){appReplacements.push(url);}},history:{replaceState(a,b,url){context.location.href=url;}},document:{getElementById:node,createElement:()=>({})}};
vm.runInNewContext(code,context);
for(const id of ['cctvNext','cctvNext','cctvPrevious','cctvReload'])node(id).events.click();
assert.deepEqual(replacements.map(url=>new URL(url).searchParams.get('channel')),['6043','6044','99','6044','6044']);
assert.equal(node('cctvVideoTitle').textContent,node('cameraTitle').textContent);
vm.runInNewContext(page.match(/<script id="rev161-cctv-exit">([\s\S]*?)<\/script>/)[1],context);
node('cctvClose').events.click({preventDefault(){}});
assert.deepEqual(appReplacements,['https://gusibzo.github.io/1560-timetable/index.html']);
const registrations=[];
let updated=0;
vm.runInNewContext(page.match(/<script id="rev162-viewer-update">([\s\S]*?)<\/script>/)[1],{URLSearchParams,location:{search:''},navigator:{serviceWorker:{register(url,options){registrations.push([url,options.updateViaCache]);return Promise.resolve({update(){updated++;}});}}}});
await new Promise(resolve=>setImmediate(resolve));
assert.match(registrations[0][0],/^\.\/sw\.js\?v=(?:162|169|173)$/);
assert.equal(registrations[0][1],'none');
assert.equal(updated,1);
console.log('Rev162: camera switches replace history, full provider header is masked, X exits after switching, viewer updates itself');
