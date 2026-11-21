(() => {
  if (!/Android/i.test(navigator.userAgent)) return;
  for (const link of document.querySelectorAll("[data-route-video]")) {
    const route = link.dataset.routeVideo;
    if (route !== "A" && route !== "B") continue;
    const guide = new URL("./route-video.html", document.baseURI);
    guide.hash = "record-" + route;
    link.href = `intent://record/${route}#Intent;scheme=routevideo1560ab;package=kr.palcheonjo.routevideo1560.ab;`
      + "S.browser_fallback_url=" + encodeURIComponent(guide.href) + ";end";
    link.hidden = false;
  }
})();
