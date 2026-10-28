import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const root = process.argv[2] || '_site';
const main = readFileSync(root + '/index.html', 'utf8');
const viewer = readFileSync(root + '/cctv.html', 'utf8');
const code = main.match(/<script id="rev169-cctv-overlay">([\s\S]*?)<\/script>/)[1];
const exit = viewer.match(/<script id="rev161-cctv-exit">([\s\S]*?)<\/script>/)[1];
const nodes = new Map(), events = {}, frames = [];
function node(id) {
  if (!nodes.has(id)) nodes.set(id, {textContent:'', open:false, events:{}, children:[], style:{overflow:'auto'},
    classList:{remove(){}},
    addEventListener(name, fn) { this.events[name] = fn; },
    appendChild(child) { this.children.push(child); child.parent=this; },
    remove() { this.parent.children=this.parent.children.filter(child=>child!==this); },
    showModal() { this.open=true; }, close() { this.open=false; },
    setAttribute(name) { if(name==='open')this.open=true; }, removeAttribute(name) { if(name==='open')this.open=false; },
    focus() { this.focused=true; }});
  return nodes.get(id);
}
const origin='https://gusibzo.github.io';
const url=origin+'/1560-timetable/index.html?v=169';
const links=[...main.matchAll(/<a class="traffic-choice [^"]+"[^>]*href="(\.\/cctv\.html\?[^\"]+)"/g)].map((match,index)=>{
  const link=node('link'+index);
  link.href=new URL(match[1].replaceAll('&amp;','&'),url).href;
  link.querySelector=()=>({textContent:'camera '+index});
  return link;
});
assert.equal(links.length,4);
const context={URL,location:{href:url,origin},
  window:{addEventListener(name,fn){events[name]=fn;}},
  document:{documentElement:node('html'),getElementById:node,
    querySelectorAll(){return links;},createElement(name){
      assert.equal(name,'iframe');const frame=node('frame'+frames.length);
      frame.contentWindow={};frames.push(frame);return frame;
    }}};
vm.runInNewContext(code,context);
function click(link,overrides={}) {
  const event={button:0,preventDefault(){this.defaultPrevented=true;},...overrides};
  link.events.click(event);return event;
}
const timetable=node('timetable');timetable.selectedTrip=3;
for (const link of links) {
  assert.equal(click(link).defaultPrevented,true);
  const frame=frames.at(-1);
  assert.equal(node('cctvOverlay').open,true);
  assert.equal(new URL(frame.src).searchParams.get('embedded'),'1');
  assert.equal(new URL(frame.src).searchParams.get('v'),'169');
  assert.equal(node('html').style.overflow,'hidden');
  // Neither cross-origin content nor a stale/different child can close it.
  for(const message of [
    {origin:'https://rtt.map.naver.com',source:frame.contentWindow},
    {origin,source:{}},
  ]) events.message({...message,data:{type:'1560-cctv-close'}});
  assert.equal(node('cctvOverlay').open,true);
  node('cctvOverlayClose').events.click();
  assert.equal(node('cctvOverlay').open,false);
  assert.equal(node('cctvOverlayBody').children.length,0,'Playback frames must be removed');
  assert.equal(node('html').style.overflow,'auto');
  assert.equal(timetable.selectedTrip,3,'Timetable state must survive without navigation');
  assert.equal(context.location.href,url);
}
assert.equal(click(links[0],{ctrlKey:true}).defaultPrevented,undefined);
click(links[0]);
events.message({origin,source:frames.at(-1).contentWindow,data:{type:'1560-cctv-close'}});
assert.equal(node('cctvOverlay').open,false);
click(links[0]);
let prevented=false;node('cctvOverlay').events.cancel({preventDefault(){prevented=true;}});
assert.ok(prevented);assert.equal(node('cctvOverlay').open,false);

// Embedded viewer exits notify their owner; standalone viewers use the link.
const messages=[],navigations=[];
const childWindow={parent:{postMessage(data,target){messages.push([data.type,target]);}}};
vm.runInNewContext(exit,{URL,URLSearchParams,window:childWindow,document:{getElementById:node},
  location:{href:origin+'/1560-timetable/cctv.html?embedded=1',search:'?embedded=1',origin,replace(value){navigations.push(value);}}});
node('cctvClose').events.click({preventDefault(){}});
assert.deepEqual(messages,[['1560-cctv-close',origin]]);
assert.deepEqual(navigations,[]);
assert.match(viewer,/\.cctv-embedded #cctvFrame\{[^}]*top:-100px/);
assert.match(viewer,/register\('\.\/sw\.js\?v=169'/);
console.log('Rev169: all CCTV entries close in place, remove playback/history frames, preserve timetable state, and reject unrelated messages');
