(() => {
  if (!/Android/i.test(navigator.userAgent)) return;
  const guide = new URL("./route-video.html", document.baseURI).href;
  const launch = "intent://record#Intent;scheme=routevideo1560;package=kr.palcheonjo.routevideo1560;";
  for (const link of document.querySelectorAll("[data-route-video]")) {
    link.href = launch + "S.browser_fallback_url=" + encodeURIComponent(guide) + ";end";
  }
})();
