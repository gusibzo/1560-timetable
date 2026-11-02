import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';
const page=readFileSync((process.argv[2]||'_site')+'/alarm.html','utf8');
const core=page.match(/<script id="alarm-core">([\s\S]*?)<\/script>/)[1];
const app=page.match(/<script id="alarm-app">([\s\S]*?)<\/script>/)[1];
new vm.Script(app);
const shared={};vm.runInNewContext(core+';this.C=AlarmCore;',shared);const C=shared.C;
assert.equal(C.volumeLevel(300),3);assert.equal(C.volumeLevel(100),1);assert.equal(C.volumeLevel(1000),3);
assert.equal(C.volumeLevel(-10),.1);assert.equal(C.volumeLevel(undefined),2);
const alarms=[{volume:80},{volume:100}],settings={};C.upgradeVolumeScale(alarms,settings);
assert.deepEqual(alarms.map(a=>a.volume),[160,200]);C.upgradeVolumeScale(alarms,settings);
assert.deepEqual(alarms.map(a=>a.volume),[160,200],'Volume migration must run only once');
assert.deepEqual({...C.rampPlan(300,true)},{from:.6,to:3,seconds:30});
assert.deepEqual({...C.rampPlan(300,false)},{from:3,to:3,seconds:0});
assert.match(page,/id="edVol"[^>]*max="300"/);

// The real alarm scheduler must ramp to the boosted target, not stop at 100%.
const gainCalls=[],scheduled=[];
const context={currentTime:12,state:'running',createGain:()=>({connect(){},gain:{setValueAtTime:(...a)=>gainCalls.push(['set',...a]),linearRampToValueAtTime:(...a)=>gainCalls.push(['ramp',...a])}})};
const start=app.slice(app.indexOf('  function startSound(a)'),app.indexOf('  function stopSound()'));
vm.runInNewContext('var ringGain,ringTimer;'+start+';startSound({volume:300,ramp:true,sound:"bird"});',{
  C,audio:()=>context,master:{},stopPreview(){},cycle:(kind,t)=>{scheduled.push([kind,t]);return 1;},setInterval:()=>1});
assert.deepEqual(gainCalls,[['set',.6,12],['ramp',3,42]]);assert.ok(scheduled.length);

// The shared output gain reaches a compressor before the physical destination.
const graph=app.slice(app.indexOf('  var ctx = null, master'),app.indexOf('  function unlockAudio()'));
const masterConnections=[],limiterConnections=[];
const compressor={threshold:{},knee:{},ratio:{},attack:{},release:{},connect:n=>limiterConnections.push(n)};
const hardware={};
class AudioContext{constructor(){this.destination=hardware;}createGain(){return {connect:n=>masterConnections.push(n)};}createDynamicsCompressor(){return compressor;}}
vm.runInNewContext(graph+';audio();',{window:{AudioContext}});
assert.equal(masterConnections[0],compressor);assert.equal(limiterConnections[0],hardware);assert.equal(compressor.ratio.value,20);

const output=app.slice(app.indexOf('  /* ---------- audio output'),app.indexOf('  /* ---------- editor'));
function fixture({supported=true,picker=true,deny=false,abort=false,missing=false}={}){
  const elements={},settings={outputDeviceId:'',outputDeviceLabel:''},routes=[];let saves=0;
  const element=()=>({hidden:true,value:'',textContent:'',innerHTML:'',children:[],listeners:{},appendChild(e){this.children.push(e);},setAttribute(k,v){this[k]=v;},addEventListener(n,fn){this.listeners[n]=fn;}});
  for(const id of ['edOutput','outputChoose','outputStatus','speakerHelp','speakerGuide'])elements[id]=element();
  const audioContext={};if(supported)audioContext.setSinkId=async id=>{routes.push(id);if(missing&&id==='gone')throw new Error('Unplugged');};
  const media={enumerateDevices:async()=>supported?[{kind:'audiooutput',deviceId:'phone',label:'휴대폰 스피커'}]:[]};
  Object.defineProperty(media,'getUserMedia',{get(){throw new Error('Must not request microphone access');}});
  if(picker)media.selectAudioOutput=async()=>{if(deny||abort){const e=new Error('Denied');e.name=abort?'AbortError':'NotAllowedError';throw e;}return {deviceId:'phone',label:'휴대폰 스피커'};};
  const ctx={navigator:{mediaDevices:media},document:{createElement:element},$:id=>elements[id],audio:()=>audioContext,ctx:audioContext,S:()=>settings,save:()=>saves++,stopPreview(){},unlockAudio(){}};
  vm.runInNewContext(output+';this.O={chooseOutput,applyOutput,restoreOutput,refreshOutputs};',ctx);
  return {O:ctx.O,e:elements,settings,routes,get saves(){return saves;}};
}
const good=fixture();await good.O.chooseOutput();assert.deepEqual(good.routes,['phone']);assert.equal(good.settings.outputDeviceId,'phone');assert.match(good.e.outputStatus.textContent,/휴대폰 스피커/);
const unsupported=fixture({supported:false,picker:false});await unsupported.O.chooseOutput();
assert.equal(unsupported.settings.outputDeviceId,'');assert.equal(unsupported.e.speakerGuide.hidden,false);assert.match(unsupported.e.outputStatus.textContent,/직접 선택할 출력 기기가 없습니다/);
assert.deepEqual(unsupported.routes,[],'Default system route must not be falsely labelled phone speaker');
for(const config of [{deny:true},{abort:true}]){
  const f=fixture(config);await f.O.chooseOutput();assert.equal(f.settings.outputDeviceId,'');assert.deepEqual(f.routes,[]);
}
const missing=fixture({missing:true});missing.settings.outputDeviceId='gone';await missing.O.restoreOutput();
assert.deepEqual(missing.routes,['gone','']);assert.equal(missing.settings.outputDeviceId,'');
console.log('Rev184: 300% gain, one-time migration, full crescendo, compression, output selection/denial/fallback and no microphone access passed');
