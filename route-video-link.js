// Older timetable pages also open the browser recorder.
for (const link of document.querySelectorAll("[data-route-video]")) {
  const route = link.dataset.routeVideo === "A" ? "A" : "B";
  link.href = "./route-video.html?start=1#record-" + route;
}
