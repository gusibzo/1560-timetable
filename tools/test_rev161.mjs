import {readFileSync} from 'node:fs';
import {strict as assert} from 'node:assert';
import vm from 'node:vm';

const root=process.argv[2]||'_site';
const page=readFileSync(root+'/cctv.html','utf8');
const script=page.match(/<script id="rev161-cctv-exit">([\s\S]*?)<\/script>/)?.[1];
assert.ok(script);
assert.match(page,/<main class="video-window"><a id="cctvClose" href="\.\/index\.html"/,'The close link must belong to our page, outside the third-party iframe');
assert.ok(page.indexOf('id="cctvClose"')<page.indexOf('<iframe'));
for(const camera of [6043,955,100,78]){
  for(const id of ['cctvClose','cctvTimetable']){
    const events={},destinations=[];
    let prevented=false;
    vm.runInNewContext(script,{
      URL,
      location:{href:'https://gusibzo.github.io/1560-timetable/cctv.html?channel='+camera,replace(url){destinations.push(url);}},
      history:{back(){throw Error('Closing must not traverse camera history');},go(){throw Error('Closing must not traverse camera history');}},
      document:{getElementById(id){return {addEventListener(name,fn){events[id+':'+name]=fn;}};}}
    });
    events[id+':click']({preventDefault(){prevented=true;}});
    assert.equal(prevented,true);
    assert.deepEqual(destinations,['https://gusibzo.github.io/1560-timetable/index.html']);
  }
}
console.log('Rev161 close X and timetable link return directly from every entry camera without traversing history');
