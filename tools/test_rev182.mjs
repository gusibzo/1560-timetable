import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const html=readFileSync((process.argv[2]||'_site')+'/index.html','utf8');
const script=html.match(/<script id="rev182-floating-alarm">([\s\S]*?)<\/script>/)?.[1];
assert.ok(script);
const values=new Map(),classes=new Set(),frames=[];
let marker=null,boardTop=400,busTop=550,busHeight=70,mutate,resize,texts=[];
const home={appendChild(n){n.parentElement=this;}};
const board={appendChild(n){n.parentElement=this;},getBoundingClientRect:()=>({top:boardTop}),
  classList:{contains:c=>classes.has(c),add:c=>classes.add(c),remove:c=>classes.delete(c)}};
const link={parentElement:home,offsetHeight:28,
  style:{getPropertyValue:k=>values.get(k),setProperty:(k,v)=>values.set(k,v)},
  getBoundingClientRect:()=>({top:boardTop+(Number.parseFloat(values.get('--alarm-dock-top'))||0)}),
  querySelector:()=>({getBoundingClientRect:()=>({top:link.getBoundingClientRect().top+3,height:22,left:780,right:807})})};
const rows={querySelector:()=>marker};
const doc={getElementById:id=>id==='rows'?rows:link,querySelector:s=>s==='.board'?board:home,
  createTreeWalker(){let i=0;return {nextNode:()=>texts[i++]||null};},
  createRange(){let node;return {selectNodeContents:n=>node=n,getClientRects:()=>node.rects};}};
vm.runInNewContext(script,{document:doc,window:{addEventListener(){}},NodeFilter:{SHOW_TEXT:4},
  requestAnimationFrame:fn=>frames.push(fn),
  MutationObserver:class{constructor(fn){mutate=fn;}observe(){}},
  ResizeObserver:class{constructor(fn){resize=fn;}observe(){}}});
const flush=()=>{while(frames.length)frames.shift()();};
const number=(top,bottom,left=760,right=810)=>({textContent:'21:30',rects:[{top,bottom,left,right,height:bottom-top,width:right-left}]});
const iconTop=()=>boardTop+Number.parseFloat(values.get('--alarm-dock-top'))+3;
const clear=()=>{
 for(const n of texts)for(const r of n.rects)if(r.width&&r.height&&r.left<811&&r.right>776)
  assert.ok(iconTop()+22<=r.top-3.5||iconTop()>=r.bottom+3.5,'Floating icon must leave every number readable');
};
assert.equal(link.parentElement,home);
marker={getBoundingClientRect:()=>({top:busTop,height:busHeight})};mutate();flush();
assert.equal(link.parentElement,board);assert.equal(iconTop(),550,'Default is slightly above the bus center');
texts=[number(565,587),number(500,522),number(550,572,400,450)];mutate();flush();
assert.equal(iconTop(),539,'Move just above the nearby departure time');clear();
// Dense extension times still leave the icon in a clear gap.
texts=[number(500,522),number(532,546),number(565,587),number(592,606),number(610,624)];
mutate();flush();clear();
texts=[];busTop=800;mutate();mutate();assert.equal(frames.length,1);flush();
assert.equal(iconTop(),800,'Follow the next bus row');
boardTop=350;busTop=490;busHeight=66;resize();flush();assert.equal(iconTop(),488);
marker=null;mutate();flush();assert.equal(link.parentElement,home);assert.equal(classes.size,0);
console.log('Rev182: floating clock clears departure/extension numbers, follows the bus, resizes and falls back safely');
