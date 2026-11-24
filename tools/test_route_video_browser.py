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


def mp4_header_duration(data):
    """Read the movie header, rather than inferring length from fragment timestamps."""
    boxes = []
    pos = 0
    while pos < len(data):
        size = int.from_bytes(data[pos:pos + 4], "big")
        assert 8 <= size <= len(data) - pos
        kind = data[pos + 4:pos + 8]
        boxes.append(kind)
        if kind == b"moov":
            # The muxer writes mvhd as the first child of moov.
            assert data[pos + 12:pos + 16] == b"mvhd"
            version = data[pos + 16]
            assert version in (0, 1)
            tick = pos + (36 if version else 28)
            scale = int.from_bytes(data[tick:tick + 4], "big")
            length = int.from_bytes(data[tick + 4:tick + (12 if version else 8)], "big")
            duration = length / scale
        pos += size
    assert b"moof" not in boxes and boxes.index(b"moov") < boxes.index(b"mdat")
    return duration


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
          // A frame timestamp can precede the click handler's performance.now().
          const raf = window.requestAnimationFrame.bind(window);
          let firstFrame = true;
          window.requestAnimationFrame = callback => raf(time => {
            const stamp = firstFrame ? 0 : time;
            firstFrame = false;
            callback(stamp);
          });
          window.filmLabels = new Set();
          window.headingColors = {};
          window.badgeColors = {};
          window.frameSync = {matched: 0, empty: 0, errors: []};
          let frame;
          const checkFrame = () => {
            if (!frame?.heading?.startsWith("운행 ")) return;
            const first = frame.vehicles[0];
            const actual = frame.heading + (frame.seats || "");
            const count = frame.heading.split("대")[0] + "대";
            const number = first?.number === "번호 미상" ? first.number : first?.number + "호";
            const expected = first ? count + "  ·  " + number + "  ·  잔여 " + first.seats : count;
            if (actual !== expected) {
              if (window.frameSync.errors.length < 10) window.frameSync.errors.push({actual, expected});
            } else if (first) window.frameSync.matched++;
            else window.frameSync.empty++;
          };
          const fillRect = CanvasRenderingContext2D.prototype.fillRect;
          CanvasRenderingContext2D.prototype.fillRect = function(x, y, w, h) {
            if (this.canvas.id === "film" && x === 0 && y === 0 &&
                w === this.canvas.width && h === this.canvas.height) {
              checkFrame();
              frame = {vehicles: []};
            }
            return fillRect.call(this, x, y, w, h);
          };
          const fill = CanvasRenderingContext2D.prototype.fillText;
          CanvasRenderingContext2D.prototype.fillText = function (text, ...args) {
            if (this.canvas.id === "film") window.filmLabels.add(text);
            if (this.canvas.id === "film" && text.startsWith("잔여 ")) {
              window.headingColors[text] = this.fillStyle;
            }
            if (this.canvas.id === "film" && frame) {
              const [x, y] = args;
              if (y === 256 && text.startsWith("운행 ")) frame.heading = text;
              if (y === 256 && text.startsWith("잔여 ")) frame.seats = text;
              if (x === 86 && /^(\\d+석|미제공)$/.test(text)) {
                frame.badge = text;
                window.badgeColors[text] = this.fillStyle;
              }
              else if (x === 86 && frame.badge !== undefined) {
                const middle = y - 32;
                if (middle - 33 >= 372 && middle + 38 <= this.canvas.height) {
                  frame.vehicles.push({number: text, seats: frame.badge});
                }
                delete frame.badge;
              }
            }
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
                     enumerate([("3452", 18), ("6771", 19), ("6789", None), ("1004", 20),
                                ("1005", 10), ("1006", 21), ("1007", 11), ("1008", 44),
                                ("1234", 45), ("3486", 0), ("1012", 12), ("1013", 13)])]
            # Feed order can differ from stop order. The heading follows the painted row.
            if mode == "clustered":
                for bus, i in zip(buses, [0, 0, 0, 1, 1, 4, 5, 7]):
                    bus.update(seq=positions[i]["seq"], stationId=positions[i]["id"])
            buses.reverse()
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
                "운행 12대  ·  3452호  ·  ", "잔여 18석", "운행 12대  ·  6771호  ·  ", "잔여 19석",
                "신분당선강남역(중) 방면", "경희대학교 방면"} <= labels
        assert await page.evaluate("window.headingColors") == {
            "잔여 45석": "#165532", "잔여 0석": "#be2030", "잔여 미제공": "#414c5a",
            "잔여 20석": "#0066ff", "잔여 10석": "#be2030", "잔여 21석": "#165532",
            "잔여 11석": "#ad226d", "잔여 44석": "#165532",
            "잔여 12석": "#ad226d", "잔여 13석": "#0066ff", "잔여 18석": "#0066ff", "잔여 19석": "#0066ff",
        }
        badges = await page.evaluate("window.badgeColors")
        assert {seats for seats, color in badges.items() if color == "#0066ff"} == {"13석", "18석", "19석", "20석"}
        sync = await page.evaluate("window.frameSync")
        assert not sync["errors"] and sync["matched"] > 10 and sync["empty"] > 10, sync
        print(f"1560{route}: {sync['matched']} matched frames, {sync['empty']} without visible vehicles", flush=True)
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
        assert path.suffix == ".mp4" and abs(mp4_header_duration(path.read_bytes()) - duration) < 0.5
        assert "영상 길이" in await page.locator("#status").inner_text()
        # Sample the encoded pixels at the route line on its two directions.
        for second, is_outbound in [(0, True), (int(duration) - 1, False)]:
            sample = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path),
                "-ss", str(second), "-vf", "crop=2:2:220:468,scale=1:1,format=rgb24",
                "-frames:v", "1", "-f", "rawvideo", "-"])
            assert len(sample) == 3
            red, green, blue = sample
            assert blue > red + 50 if is_outbound else red > green + 50
        # The 18- and 19-seat badges are blue next to red bus bodies in the opening frame.
        for x, y, expected in [(153, 427, (196, 22, 56)), (153, 555, (196, 22, 56)),
                               (55, 407, (229, 240, 255)), (55, 535, (229, 240, 255)),
                               (55, 663, (238, 241, 245)), (55, 791, (229, 240, 255)), (55, 919, (190, 32, 48)),
                               (55, 1047, (213, 241, 207))]:
            pixel = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path),
                "-vf", f"crop=2:2:{x}:{y},scale=1:1,format=rgb24", "-frames:v", "1",
                "-f", "rawvideo", "-"])
            assert len(pixel) == 3 and all(abs(a-b) < 28 for a, b in zip(pixel, expected)), (x, y, pixel)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], check=True)
        print(file.suggested_filename, stream["codec_name"], round(max(times)-min(times), 1), "seconds", flush=True)
        assert not errors, errors
        mode = "clustered"
        await page.locator("#start").click()
        await page.locator("#stop").wait_for()
        assert not await page.locator("#save").is_visible()
        await page.wait_for_timeout(1400)
        await page.locator("#stop").click()
        await page.wait_for_function("document.querySelector('#status').textContent.includes('여기까지')")
        async with page.expect_download() as second_download:
            await page.locator("#save").click()
        short = await second_download.value
        assert 0 < mp4_header_duration((await short.path()).read_bytes()) < 10
        assert not (await page.evaluate("window.frameSync"))["errors"]
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
