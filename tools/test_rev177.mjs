import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const root=process.argv[2]||'_site';
const main=readFileSync(root+'/index.html','utf8');
const page=readFileSync(root+'/alarm.html','utf8');
const sw=readFileSync(root+'/sw.js','utf8');
// The timetable keeps its side tools and gains one alarm shortcut.
assert.equal((main.match(/id="alarmQuick" href="\.\/alarm\.html"/g)||[]).length,1);
assert.match(main,/id="gpsQuick"[^>]*>🧭<\/button>\s*<a class="side-tool" id="alarmQuick"/);
assert.match(sw,/notificationclick/);
assert.match(page,/<title>1560 알람/);
for(const tab of ['alarm','clock','more']) assert.match(page,new RegExp(`data-tab="${tab}"`));
const core=page.match(/<script id="alarm-core">([\s\S]*?)<\/script>/)[1];
const ctx={};vm.runInNewContext(core+';this.C=AlarmCore;',ctx);
const C=ctx.C;
const at=(y,mo,d,h,mi)=>new Date(y,mo-1,d,h,mi,0,0);
const base={h:4,m:45,days:[],date:null,enabled:true,snoozeUntil:null};
// One-time alarm: later today, otherwise tomorrow.
assert.equal(+C.nextTrigger(base,at(2026,11,1,3,0)),+at(2026,11,1,4,45));
assert.equal(+C.nextTrigger(base,at(2026,11,1,15,30)),+at(2026,11,2,4,45));
// Weekday repeat skips the weekend (2026-11-01 is a Sunday).
assert.equal(+C.nextTrigger({...base,days:[1,2,3,4,5]},at(2026,11,1,15,30)),+at(2026,11,2,4,45));
assert.equal(+C.nextTrigger({...base,days:[1,2,3,4,5]},at(2026,11,6,5,0)),+at(2026,11,9,4,45));
// Dated alarms expire; snooze wins while pending.
assert.equal(C.nextTrigger({...base,h:15,m:35,date:'2026-11-01'},at(2026,11,1,15,36)),null);
assert.equal(+C.nextTrigger({...base,h:19,m:0,date:'2026-11-01'},at(2026,11,1,15,30)),+at(2026,11,1,19,0));
const snoozed=+at(2026,11,1,4,55);
assert.equal(+C.nextTrigger({...base,snoozeUntil:snoozed},at(2026,11,1,4,50)),snoozed);
// Due detection across a throttled minute, ignoring disabled alarms.
const due=C.dueAlarms([{...base},{...base,h:4,m:46,enabled:false}],at(2026,11,1,4,44),new Date(+at(2026,11,1,4,45)+20000),300000);
assert.equal(due.length,1);assert.equal(due[0].late,false);
assert.equal(C.dueAlarms([base],at(2026,11,1,4,40),at(2026,11,1,4,44),300000).length,0);
assert.equal(C.dueAlarms([base],at(2026,11,1,4,40),at(2026,11,1,4,52),300000)[0].late,true);
// Header text like the phone clock (\"5분\").
assert.equal(C.untilText(5*60000),'5분');
assert.equal(C.untilText(5*60000+50000),'5분');
assert.equal(C.untilText((3*60+20)*60000),'3시간 20분');
assert.equal(C.untilText((26*60)*60000),'1일 2시간');
assert.equal(C.relDay(at(2026,11,2,4,45),at(2026,11,1,15,30)),'내일');
assert.equal(C.repeatText([1,2,3,4,5]),'평일');
assert.deepEqual({...C.formatTime(15,35,false)},{ap:'오후',hm:'3:35'});
// The main-page badge shows the nearest enabled alarm.
const badge=main.match(/<script id="rev177-alarm-shortcut-time">([\s\S]*?)<\/script>/)[1];
const label={textContent:''},link={attrs:{},setAttribute(k,v){this.attrs[k]=v;}};
const store={'bus1560.alarm.v1':JSON.stringify({alarms:[{...base,enabled:false,h:3,m:55},{...base},{...base,h:19,m:0,date:'2026-11-01'}]})};
class FakeDate extends Date{constructor(...a){super(...(a.length?a:[+at(2026,11,1,15,30)]));}static now(){return +at(2026,11,1,15,30);}}
vm.runInNewContext(badge,{document:{getElementById:id=>id==='alarmQuickTime'?label:link},localStorage:{getItem:k=>store[k]??null},window:{addEventListener(){}},setInterval(){},Date:FakeDate,JSON,String,Array});
assert.equal(label.textContent,'19:00');
console.log('Rev177: alarm page, scheduling (one-time/weekday/dated/snooze), due detection and timetable shortcut passed');
