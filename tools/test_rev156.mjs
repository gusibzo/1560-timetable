import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const root = process.argv[2] || '_site';
const html = readFileSync(root + '/index.html', 'utf8');
const script = html.match(/<script id="rev156-open-at-bus">([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'The published page must include the opening behavior');

function fixture({rowTop=900, pageHeight=1800, inset=0, extension=false}={}) {
  const events = {}, frames = [], scrolls = [];
  let spacer = null, syncs = 0;
  const window = {
    scrollY:0, scrollX:12, innerHeight:800,
    addEventListener(name, fn) { (events[name] ||= []).push(fn); },
    scrollTo(value) { scrolls.push(value); this.scrollY = value.top; }
  };
  const header = {getBoundingClientRect:()=>({height:300})};
  const row = {getBoundingClientRect:()=>({top:rowTop-window.scrollY,height:80})};
  const marker = {closest:()=>row};
  const scroller = {get scrollHeight(){return pageHeight+parseFloat(spacer?.style.height||0);}};
  const document = {
    hidden:false, readyState:'loading', scrollingElement:scroller,
    addEventListener:window.addEventListener,
    getElementById:()=>spacer,
    createElement:()=>({style:{},setAttribute(){}}),
    querySelector(selector) {
      if(selector.includes('td.next')) return this.hasMarker ? marker : null;
      if(selector==='.sticky-head') return header;
      if(selector==='main.wrap') return {appendChild(el){spacer=el;}};
      return null;
    },
    hasMarker:true
  };
  const history = {scrollRestoration:'auto'};
  vm.runInNewContext(script, {window,document,history,
    getComputedStyle:()=>({top:String(inset)}),
    requestAnimationFrame:fn=>frames.push(fn),
    rev23SyncCounter:()=>{syncs++;},
  });
  return {window,document,history,scrolls,
    emit(name){for(const fn of events[name]||[]) fn();},
    flush(){while(frames.length) frames.shift()();},
    get spaceHeight(){return parseFloat(spacer?.style.height||0);},
    get syncs(){return syncs;}
  };
}

const middle=fixture({inset:12});
middle.emit('pageshow');middle.flush();
assert.equal(middle.window.scrollY,580);
assert.equal(middle.scrolls[0].left,12);
assert.equal(middle.spaceHeight,0);
assert.equal(middle.history.scrollRestoration,'manual');
assert.equal(middle.syncs,1);

const last=fixture({rowTop:1700});
last.emit('pageshow');last.flush();
assert.equal(last.window.scrollY,1392);
assert.equal(last.spaceHeight,392,'Final row needs enough trailing space');
last.emit('pageshow');last.flush();
assert.equal(last.spaceHeight,392,'Repeated opening must not grow the gap');

const early=fixture({rowTop:200});
early.emit('pageshow');early.flush();
assert.equal(early.window.scrollY,0,'Never request a negative scroll');

const user=fixture();
user.emit('pageshow');user.emit('touchstart');user.flush();
assert.equal(user.scrolls.length,0,'User scrolling cancels a pending jump');
user.document.hidden=true;user.emit('visibilitychange');user.flush();
assert.equal(user.scrolls.length,0);
user.document.hidden=false;user.emit('visibilitychange');user.flush();
assert.equal(user.scrolls.length,1,'Returning to the app realigns the bus');

const absent=fixture();absent.document.hasMarker=false;
absent.emit('pageshow');absent.flush();
assert.equal(absent.scrolls.length,0,'Do not jump when there is no current bus');
console.log('Rev156 opening, sticky offset, last row, restoration and user-scroll checks passed');
