import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const page=readFileSync((process.argv[2]||'_site')+'/alarm.html','utf8');
const core=page.match(/<script id="alarm-core">([\s\S]*?)<\/script>/)[1];
const app=page.match(/<script id="alarm-app">([\s\S]*?)<\/script>/)[1];
new vm.Script(app);
const scheduler=app.slice(app.indexOf('  /* ---------- scheduler'),app.indexOf('  function tidy()'));
const at=(d,h,m)=>+new Date(2026,10,d,h,m);
const alarm=()=>({id:'a',h:21,m:40,days:[],date:null,enabled:true,armedSince:at(7,21,30)});
function boot(saved,when){
  const clock={now:when},rings=[],storage={value:JSON.stringify(saved)};
  class Clock extends Date{constructor(...args){super(...(args.length?args:[clock.now]));}static now(){return clock.now;}}
  const c={Date:Clock,state:JSON.parse(storage.value),ringing:null,renderList(){},renderRemaining(){},
    save(){storage.value=JSON.stringify(c.state);},
    ring(a,late){rings.push({id:a.id,at:a.pendingAt,late});c.ringing=a;},
  };
  vm.createContext(c);vm.runInContext(core+';var C=AlarmCore;'+scheduler+';this.tick=tick;this.core=C;',c);
  return {c,clock,rings,storage};
}

// Recreate a process after the screenshot's 21:40 -> 21:53 interruption.
let run=boot({alarms:[alarm()]},at(7,21,39));run.c.tick();
assert.equal(run.rings.length,0);
run=boot(JSON.parse(run.storage.value),at(7,21,53));run.c.tick();
assert.deepEqual(run.rings,[{id:'a',at:at(7,21,40),late:true}]);
assert.equal(run.c.core.remainingText(run.c.state.alarms[0],new Date(at(7,21,53)),true),'알람 울리는 중');
run.c.tick();assert.equal(run.rings.length,1,'The same occurrence must not ring twice per session');

// A page reload while a sound was pending must recover that pending occurrence.
run=boot(JSON.parse(run.storage.value),at(7,21,54));run.c.tick();
assert.equal(run.rings.length,1);assert.equal(run.rings[0].at,at(7,21,40));

// After the recovery window, preserve a visible missed alarm instead of tomorrow.
run=boot({alarms:[alarm()],checkedAt:at(7,21,39)},at(7,22,0));run.c.tick();
assert.equal(run.rings.length,0);
assert.equal(run.c.state.alarms[0].enabled,false);
assert.match(run.c.core.remainingText(run.c.state.alarms[0],new Date(at(7,22,0))),/놓친 알람.*21:40/);
run=boot(JSON.parse(run.storage.value),at(8,6,0));run.c.tick();
assert.match(run.c.core.remainingText(run.c.state.alarms[0],new Date(at(8,6,0))),/놓친 알람/);

// A long pause must not discard its checkpoint, including dated alarms.
run=boot({alarms:[{...alarm(),date:'2026-11-07'}],checkedAt:at(7,20,0)},at(8,6,0));run.c.tick();
assert.equal(run.c.state.alarms[0].missedAt,at(7,21,40));

// Alarms deliberately created after today's selected time still target tomorrow.
run=boot({alarms:[{...alarm(),armedSince:at(7,21,45)}],checkedAt:at(7,21,0)},at(7,21,53));run.c.tick();
assert.equal(run.rings.length,0);assert.equal(run.c.state.alarms[0].missedAt,undefined);

// Repeated schedules recover the latest matching day after several days offline.
run=boot({alarms:[{...alarm(),days:[1,2,3,4,5],armedSince:at(2,19,0)}],checkedAt:at(2,20,0)},at(6,21,45));run.c.tick();
assert.equal(run.rings[0].at,at(6,21,40));

// The actual audio retry interface reports a suspended context without implying playback.
const status={},button={};
const update=app.slice(app.indexOf('  function updateRingAudio()'),app.indexOf("  $('ringAudioRetry').addEventListener"));
const c={ringing:{id:'a'},ctx:{state:'suspended'},$:id=>id==='ringAudioStatus'?status:button};
vm.runInNewContext(update+';this.update=updateRingAudio;',c);c.update();
assert.equal(button.hidden,false);assert.match(status.textContent,/소리 재생/);
c.ctx.state='running';c.update();assert.equal(button.hidden,true);assert.equal(status.textContent,'');
console.log('Rev188: reload/suspension recovery, persistent missed alarms, no duplicate occurrence, edits, repeats and blocked audio status passed');
