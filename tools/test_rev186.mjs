import {readFileSync,existsSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const root=process.argv[2]||'_site';
const page=readFileSync(root+'/alarm.html','utf8');
const app=page.match(/<script id="alarm-app">([\s\S]*?)<\/script>/)[1];
const audioPart=app.slice(app.indexOf('  var ANIMAL_SOUNDS'),app.indexOf('  /* ---------- wake lock'));
const started=[];
const ctx={currentTime:1,createBufferSource(){return {connect(){},start(t){started.push(t)}}},decodeAudioData:async()=>({duration:2.5})};
const c={ctx,master:{},audio:()=>ctx,fetch:async url=>({ok:existsSync(root+'/'+url.replace(/^\.\//,'').split('?')[0]),arrayBuffer:async()=>new ArrayBuffer(1)}),Promise,Error,setTimeout,clearTimeout,tone(){},$:()=>({textContent:'',setAttribute(){}})};
vm.runInNewContext(audioPart+';this.api={loadAnimal,cycle};',c);
for(const kind of ['lion','tiger','tigerGrowl','rooster','roosterFarm']){await c.api.loadAnimal(kind);assert.equal(c.api.cycle(kind,2,{}),2.5,kind);}
assert.equal(started.length,5);
const sw=readFileSync(root+'/sw.js','utf8');
for(const file of ['lion-roar.mp3','tiger-roar.mp3','tiger-growl.mp3','rooster-farm.mp3','rooster.mp3?v=186']) assert.ok(sw.includes(file));
assert.match(page,/bus1560\.alarm\.v1/);
console.log('Rev186 animal files load, decode and schedule with existing alarm storage');
