"""Record each whole route and verify that a mobile-size Chrome page exports decodable video."""
import asyncio
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile
from threading import Thread

from playwright.async_api import async_playwright


async def record_route(browser, url, route, output_dir):
    context = await browser.new_context(viewport={"width": 390, "height": 844},
                                        is_mobile=True, has_touch=True, accept_downloads=True)
    try:
        page = await context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        # Check the exact text painted into the video, including first/turn/last
        # stops. A fresh fixture places a vehicle by the first stop for both routes.
        await page.add_init_script("""
          window.filmLabels = new Set();
          const fill = CanvasRenderingContext2D.prototype.fillText;
          CanvasRenderingContext2D.prototype.fillText = function (text, ...args) {
            if (this.canvas.id === "film") window.filmLabels.add(text);
            return fill.call(this, text, ...args);
          };
        """)
        # The deployed snapshot is already stale, as in the reported recording.
        # Only the on-demand GBIS response should supply vehicle and seat labels.
        async def stale_stations(request):
            response = await request.fetch()
            data = await response.json()
            data["observation"] = {"at": "2020-01-01T00:00:00Z", "buses": []}
            await request.fulfill(json=data)

        positions = json.loads((Path(__file__).resolve().parents[1] /
                                f"route-video-data/{route}.json").read_text())["stops"]
        mode = "unavailable"
        async def bus_feed(request):
            if mode == "unavailable":
                await request.fulfill(status=503, body="")
                return
            now = await page.evaluate("new Date().toISOString()")
            buses = [{"seq": positions[i]["seq"], "stationId": positions[i]["id"],
                      "vehicle": vehicle, "seats": seats} for i, (vehicle, seats) in
                     enumerate([("1234", 45), ("5678", 0), ("6789", None)])]
            await request.fulfill(json={"at": now, "route": route, "buses": [] if mode == "empty" else buses})

        await page.route(f"**/route-video-data/{route}.json", stale_stations)
        await page.route(f"**/api/gbis/{route}", bus_feed)
        await page.goto(f"{url}/route-video.html?start=1#record-{route}")
        await page.get_by_text("최근 차량 정보를 받지 못했습니다.", exact=False).wait_for()
        assert not await page.locator("#stop").is_visible()
        mode = "empty"
        await page.get_by_role("button", name="차량 다시 조회").click()
        await page.get_by_text("표시된 운행 차량이 0대입니다.", exact=False).wait_for()
        assert not await page.locator("#stop").is_visible()
        mode = "running"
        await page.get_by_role("button", name="차량 다시 조회").click()
        await page.locator("#stop").wait_for(timeout=12000)
        await page.locator("#save").wait_for(timeout=120000)
        assert "마지막 정류장" in await page.locator("#status").inner_text()
        labels = set(await page.evaluate("Array.from(window.filmLabels)"))
        assert {"1560" + route, "기점", "회차", "종점", "경희대정문", "1234", "45석", "0석", "미제공",
                "운행 3대  ·  1234호  ·  잔여 45석",
                "신분당선강남역(중) 방면", "경희대학교 방면"} <= labels
        assert not any("녹화" in label for label in labels)
        assert sum(bool(re.fullmatch(r"\d{4}\.\d{2}\.\d{2} \([일월화수목금토]\) \d{2}:\d{2}:\d{2}", label)) for label in labels) > 10
        async with page.expect_download() as download:
            await page.locator("#save").click()
        file = await download.value
        assert file.suggested_filename.startswith("1560" + route + "_")
        path = output_dir / file.suggested_filename
        await file.save_as(path)
        probe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height:packet=pts_time", "-of", "json", str(path)])
        details = json.loads(probe)
        stream = details["streams"][0]
        times = [float(p["pts_time"]) for p in details["packets"] if "pts_time" in p]
        duration = max(times) - min(times)
        assert (stream["width"], stream["height"]) == (720, 1140) and 47 < duration < 56
        # Sample the encoded pixels at the route line on its two directions.
        for second, is_outbound in [(0, True), (int(duration) - 1, False)]:
            sample = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path),
                "-ss", str(second), "-vf", "crop=2:2:220:468,scale=1:1,format=rgb24",
                "-frames:v", "1", "-f", "rawvideo", "-"])
            assert len(sample) == 3
            red, green, blue = sample
            assert blue > red + 50 if is_outbound else red > green + 50
        # The first bus body and green seat badge must survive video encoding.
        for x, y, channel in [(153, 427, 0), (55, 407, 1)]:
            pixel = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path),
                "-vf", f"crop=2:2:{x}:{y},scale=1:1,format=rgb24", "-frames:v", "1",
                "-f", "rawvideo", "-"])
            assert len(pixel) == 3 and pixel[channel] > min(pixel) + 15, (x, y, pixel)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], check=True)
        print(file.suggested_filename, stream["codec_name"], round(max(times)-min(times), 1), "seconds", flush=True)
        assert not errors, errors
        await page.locator("#start").click()
        await page.wait_for_timeout(1400)
        await page.locator("#stop").click()
        await page.wait_for_function("document.querySelector('#status').textContent.includes('여기까지')")
    finally:
        await context.close()


async def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    handler = partial(SimpleHTTPRequestHandler, directory=root)
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server, tempfile.TemporaryDirectory() as temp:
        Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_port}"
        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path=os.getenv("CHROME_BIN") or shutil.which("google-chrome"),
                args=["--no-sandbox", "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
                      "--disable-backgrounding-occluded-windows"])
            try:
                await asyncio.gather(*(record_route(browser, url, route, Path(temp)) for route in "AB"))
            finally:
                await browser.close()
        server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
