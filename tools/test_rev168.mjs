import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const root = process.argv[2] || '_site';
const main = readFileSync(root + '/index.html', 'utf8');
const page = readFileSync(root + '/cctv.html', 'utf8');
assert.match(main, /id="kyoboCctvLink" href="\.\/cctv\.html\?channel=6929&amp;v=(?:168|169|173|174)"/);
assert.match(main, /교보문고 사거리 CCTV/);
const data = page.match(/<script id="cctvCameraData" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code = page.match(/<script id="rev160-cctv-controller">([\s\S]*?)<\/script>/)[1];
const nodes = new Map(), loads = [], exits = [];
function node(id) {
  if (!nodes.has(id)) nodes.set(id, {textContent:'', value:'', events:{}, children:[],
    addEventListener(name, fn) { this.events[name] = fn; },
    setAttribute(name, value) { this[name] = value; },
    appendChild(child) { this.children.push(child); }});
  return nodes.get(id);
}
node('cctvCameraData').textContent = data;
node('cctvFrame').contentWindow = {location:{replace(url) { loads.push(new URL(url)); }}};
const location = {href:'https://gusibzo.github.io/1560-timetable/cctv.html?channel=6929&v=168',
  search:'?channel=6929&v=168', replace(url) { exits.push(url); }};
const context = {setTimeout(){return 1;},clearTimeout(){},URL, URLSearchParams, location,
  history:{replaceState(a,b,url) { location.href=url; }},
  document:{getElementById:node, createElement:()=>({})}};
vm.runInNewContext(code, context);
const current = () => Object.fromEntries(loads.at(-1).searchParams);
assert.deepEqual(current(), {cctvGroupId:'94', channel:'6929', seq:'4'});
assert.equal(node('cameraTitle').textContent, '강남대로 · 교보타워R');
assert.equal(node('previousName').textContent, '논현역');
assert.equal(node('nextName').textContent, '강남역');
assert.equal(node('cameraSelect').children.length, 8, 'Only Gangnam-daero cameras belong in this road selector');
node('cctvNext').events.click();
assert.deepEqual(current(), {cctvGroupId:'94', channel:'6058', seq:'5'});
node('cctvPrevious').events.click();
node('cctvPrevious').events.click();
assert.deepEqual(current(), {cctvGroupId:'94', channel:'6057', seq:'3'});
node('cameraSelect').value='6060'; node('cameraSelect').events.change();
assert.deepEqual(current(), {cctvGroupId:'94', channel:'6060', seq:'8'});
assert.equal(node('cctvNext').disabled, true);
const count=loads.length; node('cctvNext').events.click(); assert.equal(loads.length,count);
vm.runInNewContext(page.match(/<script id="rev161-cctv-exit">([\s\S]*?)<\/script>/)[1], context);
node('cctvClose').events.click({preventDefault(){}});
assert.deepEqual(exits, ['https://gusibzo.github.io/1560-timetable/index.html']);
console.log('Rev168: Kyobo opens group 94 camera 6929, city camera navigation stays in order, X returns directly to timetable');
