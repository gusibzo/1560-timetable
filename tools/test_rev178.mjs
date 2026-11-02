import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const html=readFileSync((process.argv[2]||'_site')+'/index.html','utf8');
const script=html.match(/<script id="rev178-alarm-above-bus">([\s\S]*?)<\/script>/)?.[1];
assert.ok(script);

// Exercise actual marker transitions, including a render which discards the
// old row, extension departures and a day with no live marker.
let writes=0,callback,marker=null;
function node(name,parent=null){
  const classes=new Set();
  return {name,parentElement:parent,children:[],classList:{
    contains:c=>classes.has(c),add(c){classes.add(c);writes++;},
    remove(c){if(classes.delete(c))writes++;}
  },appendChild(child){this.insertBefore(child,null);},
  insertBefore(child,before){
    if(child.parentElement)child.parentElement.children=child.parentElement.children.filter(c=>c!==child);
    const index=before?this.children.indexOf(before):this.children.length;
    this.children.splice(index,0,child);child.parentElement=this;writes++;
  },get nextElementSibling(){const siblings=this.parentElement?.children||[];return siblings[siblings.indexOf(this)+1]||null;}};
}
const home=node('side tools'),link=node('alarm');home.appendChild(link);
const rows={querySelector(){return marker;}};
const doc={getElementById:id=>id==='rows'?rows:link,querySelector:()=>home};
const events={};
vm.runInNewContext(script,{document:doc,window:{addEventListener:(n,fn)=>events[n]=fn},
  MutationObserver:class{constructor(fn){callback=fn;}observe(){}}});
assert.equal(link.parentElement,home);
function bus(cell,extension=false){
  const m=node(extension?'extension':'time',cell);
  cell.children.push(m);m.closest=selector=>selector==='td'?cell:m;
  return m;
}
const first=node('first bus cell');marker=bus(first);callback();
assert.equal(link.parentElement,first);assert.equal(link.nextElementSibling,marker);
assert.ok(first.classList.contains('rev178-has-alarm'));
const stableWrites=writes;for(let i=0;i<20;i++)callback();
assert.equal(writes,stableWrites,'Observer must settle without repeatedly moving the link');
// Full timetable render: the link still has a reference after its old row goes away.
const second=node('new bus cell');marker=bus(second);callback();
assert.equal(link.parentElement,second);assert.equal(link.nextElementSibling,marker);
assert.ok(!first.classList.contains('rev178-has-alarm'));
marker=null;callback();assert.equal(link.parentElement,home);
const last=node('extension cell');marker=bus(last,true);callback();
assert.equal(link.parentElement,last);assert.equal(link.nextElementSibling,marker);
assert.equal(marker.children.length,0,'Bus time/route text must remain untouched');
events.pageshow();assert.equal(link.parentElement,last);
console.log('Rev178: alarm above bus, stable observer, rerender, extension and no-marker fallback passed');
