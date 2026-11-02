import {readFileSync,existsSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const root=process.argv[2]||'_site';
const page=readFileSync(root+'/alarm.html','utf8'),sw=readFileSync(root+'/sw.js','utf8');
const core=page.match(/<script id="alarm-core">([\s\S]*?)<\/script>/)[1];
const ctx={};vm.runInNewContext(core+';this.C=AlarmCore;',ctx);
for(const [h,m]of [['0','0'],['23','59'],['7','5'],['07','05']])assert.deepEqual({...ctx.C.parseTimeNumbers(h,m)},{h:+h,m:+m});
for(const [h,m]of [['24','00'],['23','60'],['-1','00'],['','10'],['07',''],['1.5','10'],['12','abc']])assert.equal(ctx.C.parseTimeNumbers(h,m),null);
assert.equal(ctx.C.nextTrigger({h:0,m:0,days:[],enabled:true},new Date(2026,10,2,23,59)).getDate(),3,'00:00 rolls into tomorrow');
for(const id of ['edHour','edMinute'])assert.match(page,new RegExp('id="'+id+'"[^>]*inputmode="numeric"'));
assert.match(page,/if \(numberMode && !readNumbers\(true\)\) return;/,'Reject invalid numbers before saving');
assert.match(page,/if \(numberMode\) return;/,'Do not read or write a hidden wheel instead of typed numbers');

// Execute the actual recording loader, playback cycle and preview cancellation.
const app=page.match(/<script id="alarm-app">([\s\S]*?)<\/script>/)[1];
const audioPart=app.slice(app.indexOf('  var ANIMAL_SOUNDS'),app.indexOf('  /* ---------- wake lock'));
const ui={edPreview:{textContent:'',setAttribute(){}},edSoundStatus:{textContent:''}};
let requests=0,sources=[],deferred,resolveFetch;
const c={currentTime:10,createBufferSource(){const s={connect(){},start(t){this.started=t;}};sources.push(s);return s;},
 createGain:()=>({gain:{value:0},connect(){},disconnect(){}}),decodeAudioData:async()=>({duration:2.6})};
const audioCtx={ctx:c,master:{},audio:()=>c,unlockAudio(){},toast(){},tone(){},$:id=>ui[id],SOUNDS:[['dog','강아지']],
 Promise,Error,setTimeout:()=>1,clearTimeout(){},fetch:async()=>{requests++;if(deferred)await new Promise(r=>resolveFetch=r);return {ok:true,arrayBuffer:async()=>new ArrayBuffer(1)};}};
vm.runInNewContext(audioPart+';this.A={loadAnimal,cycle,preview,stopPreview};',audioCtx);
await Promise.all([audioCtx.A.loadAnimal('dog'),audioCtx.A.loadAnimal('dog')]);
assert.equal(requests,1,'Reuse concurrent sound downloads');
assert.equal(audioCtx.A.cycle('dog',12,{}),2.6);assert.equal(sources[0].started,12);
assert.equal(audioCtx.A.cycle('digital',12,{}),1.1,'Existing bells remain available');
deferred=true;audioCtx.A.preview('cat',80);audioCtx.A.stopPreview();
const before=sources.length;resolveFetch();await new Promise(r=>setImmediate(r));
assert.equal(sources.length,before,'Closing preview before download completes must not start playback');
assert.equal(ui.edSoundStatus.textContent,'');
for(const kind of ['rooster','bird','dog','cat']){
 const file=root+'/audio/alarms/'+kind+'.mp3';assert.ok(existsSync(file));assert.ok(readFileSync(file).length>4096);
 assert.match(sw,new RegExp('audio/alarms/'+kind+'\\.mp3'),'Precache each local recording');
}

// Offline visits must preserve separate timetable and alarm pages.
const handlers={},saved=new Map();let online=true;
const scope='https://example.test/1560/';
const swCtx={URL,Request,Response,Headers,console,
 self:{location:{origin:'https://example.test'},registration:{scope},addEventListener:(n,fn)=>handlers[n]=fn},
 caches:{open:async()=>({put:async(k,v)=>saved.set(typeof k==='string'?k:k.url||k.href,v),match:async k=>saved.get(typeof k==='string'?k:k.url||k.href)?.clone()})},
 fetch:async req=>{if(!online)throw new Error('offline');return new Response('<html><head></head><body>'+new URL(req.url).pathname+'</body></html>',{headers:{'content-type':'text/html'}});}};
vm.runInNewContext(sw,swCtx);
async function navigate(path){let response;handlers.fetch({request:{method:'GET',mode:'navigate',url:scope+path},respondWith:p=>response=p});return (await response).text();}
await navigate('alarm.html');await navigate('');online=false;
assert.match(await navigate('alarm.html'),/1560\/alarm.html/);
assert.doesNotMatch(await navigate(''),/1560\/alarm.html/);
console.log('Rev183: numeric limits/midnight, actual audio scheduling/cancel, local sounds and separate offline pages passed');
