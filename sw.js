const CACHE_NAME="1560-timetable-rev34-v1";
const REVISION="34";
const CORE=["./","./index.html","./manifest.webmanifest"];

const OLD_GYEONGGI_BADGE='<a class="gyeonggi-badge" href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" aria-label="경기버스정보 열기"><span class="bus">🚌</span><span>경기버스</span></a>';
const NEW_FINANCE_BADGE='<button class="gyeonggi-badge" type="button" id="financeBtn" aria-haspopup="dialog" aria-controls="financeModal" aria-label="환율·주식 정보 열기" style="font-family:inherit;cursor:pointer"><span class="bus">💱</span><span>환율·주식</span></button>';
const OLD_FINANCE_BUTTON='<button type="button" id="financeBtn" aria-haspopup="dialog" aria-controls="financeModal">💱 환율·주식</button>';
const NEW_GYEONGGI_LINK='<a href="https://m.gbis.go.kr/search" target="_blank" rel="noopener noreferrer" aria-label="경기버스정보 열기">🚌 경기버스</a>';

function swapQuickLinks(html){
  return html
    .replace(OLD_GYEONGGI_BADGE,NEW_FINANCE_BADGE)
    .replace(OLD_FINANCE_BUTTON,NEW_GYEONGGI_LINK);
}

async function transformNavigationResponse(response){
  if(!response)return response;
  const contentType=response.headers.get("content-type")||"";
  if(!contentType.includes("text/html"))return response;

  const html=await response.text();
  const headers=new Headers(response.headers);
  headers.delete("content-length");
  headers.delete("content-encoding");
  headers.set("content-type","text/html; charset=utf-8");

  return new Response(swapQuickLinks(html),{
    status:response.status,
    statusText:response.statusText,
    headers
  });
}

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
        if(request.mode==="navigate"){
          const transformed=await transformNavigationResponse(fresh);
          const key=new Request(new URL("./index.html",self.registration.scope));
          cache.put(key,transformed.clone()).catch(()=>{});
          return transformed;
        }
        cache.put(request,fresh.clone()).catch(()=>{});
      }
      return fresh;
    }catch(_){
      if(request.mode==="navigate"){
        const cached=await cache.match(new URL("./index.html",self.registration.scope));
        return (await transformNavigationResponse(cached)) || Response.error();
      }
      return (await cache.match(request)) || Response.error();
    }
  })());
});
