import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const html=readFileSync((process.argv[2]||'_site')+'/index.html','utf8');
const script=html.match(/<script id="rev181-right-edge-alarm">([\s\S]*?)<\/script>/)?.[1];
assert.ok(script);
assert.doesNotMatch(html,/<script id="rev178-alarm-above-bus">/);

const values=new Map(),classes=new Set(),frames=[],events={};
let marker=null,boardTop=400,busTop=550,busHeight=70,mutate,resize;
const home={appendChild(n){n.parentElement=this;}};
const board={appendChild(n){n.parentElement=this;},getBoundingClientRect:()=>({top:boardTop}),
  classList:{contains:c=>classes.has(c),add:c=>classes.add(c),remove:c=>classes.delete(c)}};
const link={parentElement:home,offsetHeight:28,style:{getPropertyValue:k=>values.get(k),setProperty:(k,v)=>values.set(k,v)}};
const rows={querySelector:()=>marker};
const doc={getElementById:id=>id==='rows'?rows:link,querySelector:s=>s==='.board'?board:home};
vm.runInNewContext(script,{document:doc,window:{addEventListener:(n,fn)=>events[n]=fn},
  requestAnimationFrame:fn=>frames.push(fn),
  MutationObserver:class{constructor(fn){mutate=fn;}observe(){}},
  ResizeObserver:class{constructor(fn){resize=fn;}observe(){}}});
const flush=()=>{while(frames.length)frames.shift()();};
assert.equal(link.parentElement,home,'Without a live bus the ordinary shortcut remains available');
marker={getBoundingClientRect:()=>({top:busTop,height:busHeight})};mutate();flush();
assert.equal(link.parentElement,board);
assert.equal(Number.parseFloat(values.get('--alarm-dock-top'))+14,busTop-boardTop+busHeight/2,'Clock and bus centers align');
busTop=800;mutate();mutate();assert.equal(frames.length,1,'Batch repeated marker mutations');flush();
assert.equal(values.get('--alarm-dock-top'),'421px','Follow a new bus row');
boardTop=350;busTop=490;busHeight=66;resize();flush();
assert.equal(values.get('--alarm-dock-top'),'159px','Recalculate after the timetable resizes');
marker=null;mutate();flush();assert.equal(link.parentElement,home);assert.equal(classes.size,0);
console.log('Rev181: right-edge alarm alignment, bus changes, resize, batching and no-bus fallback passed');
