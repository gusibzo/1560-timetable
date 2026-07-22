const CACHE_NAME="1560-timetable-rev33-v1";
const REVISION="33";
const CORE=["./","./index.html","./manifest.webmanifest"];

self.addEventListener("install",event=>{
  event.waitUntil((async()=>{
    const cache=await caches.open(CACHE_NAME);
    try{await cache.addAll(CORE);}catch(_){/* network may be temporarily unavailable */}
    await self.skipWaiting();
  })());
});

self.addEventListener("activate",event=>{
  event.waitUntil((async()=>{
    const names=await caches.keys();
    await Promise.all(names.filter(name=>name!==CACHE_NAME).map(name=>caches.delete(name)));
    await self.clients.claim();

    // Recover phones that are still displaying an old cached revision.
    const windows=await self.clients.matchAll({type:"window",includeUncontrolled:true});
    await Promise.all(windows.map(async client=>{
      try{
        const url=new URL(client.url);
        if(url.origin!==self.location.origin)return;
        if(url.searchParams.get("swfix")===REVISION)return;
        url.searchParams.set("v",REVISION);
        url.searchParams.set("swfix",REVISION);
        await client.navigate(url.href);
      }catch(_){/* a closing tab cannot be navigated */}
    }));
  })());
});

self.addEventListener("fetch",event=>{
  const request=event.request;
  if(request.method!=="GET")return;
  const url=new URL(request.url);
  if(url.origin!==self.location.origin)return;

  event.respondWith((async()=>{
    const cache=await caches.open(CACHE_NAME);
    try{
      // Navigation is always network-first so ?v= updates cannot be trapped by an old page.
      const fresh=await fetch(request,{cache:"no-store"});
      if(fresh&&fresh.ok){
        const key=request.mode==="navigate"?new Request(new URL("./index.html",self.registration.scope)):request;
        cache.put(key,fresh.clone()).catch(()=>{});
      }
      return fresh;
    }catch(_){
      if(request.mode==="navigate"){
        return (await cache.match(new URL("./index.html",self.registration.scope))) || Response.error();
      }
      return (await cache.match(request)) || Response.error();
    }
  })());
});
