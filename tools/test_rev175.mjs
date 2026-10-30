import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const html=readFileSync((process.argv[2]||'_site')+'/index.html','utf8');
assert.match(html, /id="busBoardBtn" href="https:\/\/bus1560-board\.gusibzo\.chatgpt\.site\/" target="_top"/);
assert.match(html, /#busBoardBtn\{touch-action:manipulation!important/);
const code=html.match(/<script id="rev175-board-opening">([\s\S]*?)<\/script>/)[1];
const events={},windowEvents={},timers=[];
const link={textContent:'📋 게시판',attributes:{},addEventListener(k,fn){events[k]=fn;},setAttribute(k,v){this.attributes[k]=v;},removeAttribute(k){delete this.attributes[k];}};
vm.runInNewContext(code,{document:{getElementById(){return link;}},window:{addEventListener(k,fn){windowEvents[k]=fn;}},setTimeout(fn){timers.push(fn);return timers.length;},clearTimeout(){}});
function click(extra={}){const event={button:0,preventDefault(){this.defaultPrevented=true;},...extra};events.click(event);return event;}
// The first touch/click follows the real href; extra taps must not restart it.
assert.ok(!click().defaultPrevented);
assert.equal(link.textContent,'📋 여는 중…');assert.equal(link.attributes['aria-busy'],'true');
assert.equal(click().defaultPrevented,true);
windowEvents.pageshow();assert.equal(link.textContent,'📋 게시판');assert.equal(link.attributes['aria-busy'],undefined);
assert.ok(!click({ctrlKey:true}).defaultPrevented);assert.equal(link.textContent,'📋 게시판');
assert.ok(!click().defaultPrevented);timers.at(-1)();assert.equal(link.textContent,'📋 게시판');
console.log('Rev175: one native board click, immediate status, repeated-click guard, modifier links and return/reset passed');
