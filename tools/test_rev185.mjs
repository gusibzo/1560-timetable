import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const page=readFileSync((process.argv[2]||'_site')+'/alarm.html','utf8');
const core=page.match(/<script id="alarm-core">([\s\S]*?)<\/script>/)[1];
const app=page.match(/<script id="alarm-app">([\s\S]*?)<\/script>/)[1];
new vm.Script(app);
const shared={};vm.runInNewContext(core+';this.C=AlarmCore;',shared);const C=shared.C;
const now=new Date(2026,10,2,12,48,0); // Monday, local time, independent of host zone.
const alarm={id:'one',h:15,m:5,enabled:true,days:[],date:null};
assert.equal(C.remainingText(alarm,now),'2시간 17분 남음');
assert.equal(C.remainingText({...alarm,h:18,m:50},now),'6시간 2분 남음');
assert.equal(C.remainingText(alarm,new Date(2026,10,2,12,48,1)),C.untilText(new Date(2026,10,2,15,5)-new Date(2026,10,2,12,48,1))+' 남음','Card and next-alarm header must use the same minute rounding');
assert.equal(C.remainingText({...alarm,enabled:false},now),'알람 꺼짐');
assert.equal(C.remainingText({...alarm,date:'2026-11-01'},now),'지난 알람');
assert.equal(C.remainingText({...alarm,h:4,m:45},now),'15시간 57분 남음','Past time without a date means tomorrow');
assert.equal(C.remainingText({...alarm,days:[0,6]},now),'5일 2시간 17분 남음','Weekend repeats use the next selected day');
assert.equal(C.remainingText({...alarm,date:'2026-11-05'},now),'3일 2시간 17분 남음');
assert.equal(C.remainingText({...alarm,snoozeUntil:now.getTime()+42000},now),'42초 남음','Snooze takes priority over original time');
assert.equal(C.remainingText(alarm,new Date(2026,10,2,15,4,1)),'59초 남음');
assert.equal(C.remainingText(alarm,new Date(2026,10,2,15,4,59,950)),'1초 남음');
assert.equal(C.remainingText(alarm,new Date(2026,10,2,15,4,0)),'1분 남음');
assert.equal(C.remainingText(alarm,new Date(2026,10,2,15,5,0),true),'알람 울리는 중','A ringing alarm must not show tomorrow’s countdown');

// Exercise the actual DOM update and scheduler wiring with two independent cards.
const changes=[];
function node(id){
  let value='';return {getAttribute:()=>id,get textContent(){return value;},set textContent(text){changes.push([id,text]);value=text;}};
}
const nodes=[node('one'),node('two')];
const alarms=[{...alarm,h:12,m:49},{...alarm,id:'two',h:18,m:50}];
const list={querySelectorAll:()=>nodes};
Object.defineProperty(list,'innerHTML',{set(){throw new Error('Countdown must not rebuild the list');}});
const update=app.slice(app.indexOf('  function renderRemaining(now)'),app.indexOf('  function nextEnabled(now)'));
const context={C,$:id=>{assert.equal(id,'list');return list;},find:id=>alarms.find(a=>a.id===id),ringing:null};
vm.runInNewContext(update+';this.update=renderRemaining;',context);
context.update(now);assert.equal(nodes[0].textContent,'1분 남음');assert.equal(nodes[1].textContent,'6시간 2분 남음');
context.update(new Date(2026,10,2,12,48,1));assert.equal(nodes[0].textContent,'59초 남음');
const n=changes.length;context.update(new Date(2026,10,2,12,48,1));assert.equal(changes.length,n,'Unchanged countdowns do not mutate the DOM');
alarms[1].enabled=false;context.update(now);assert.equal(nodes[1].textContent,'알람 꺼짐');
context.ringing=alarms[0];context.update(new Date(2026,10,2,12,49));assert.equal(nodes[0].textContent,'알람 울리는 중');
assert.match(app,/function tick\(\)[\s\S]*?renderRemaining\(now\);/);
assert.match(app,/setInterval\(tick, 1000\)/);
assert.match(page,/class="remaining" data-alarm-id=/);
assert.match(page,/\.card \.side\{grid-column:2;grid-row:1\/5;/);
console.log('Rev185: per-alarm countdowns, second/minute boundaries, repeats, dates, snooze, disabled/ringing states and in-place updates passed');
