"""Record each whole route and verify that a mobile-size Chrome page exports decodable video."""
import asyncio
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
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
        await page.goto(f"{url}/route-video.html?start=1#record-{route}")
        await page.locator("#stop").wait_for(timeout=12000)
        await page.locator("#save").wait_for(timeout=120000)
        assert "마지막 정류장" in await page.locator("#status").inner_text()
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
        assert (stream["width"], stream["height"]) == (640, 1000) and max(times) - min(times) > 60
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
