#!/usr/bin/env python3
"""Prepare local assets from the repository's attributed animal recordings.
Synthetic WAVs have a 0.72 full-scale peak; playback uses USAGE_ALARM.
"""
from pathlib import Path
from html.parser import HTMLParser
import math
import re
import shutil
import struct
import wave

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "audio" / "alarms"
ASSETS = ROOT / "assets"
SOUNDS = ASSETS / "sounds"
SOUNDS.mkdir(parents=True, exist_ok=True)
ANIMALS = {
    "lion": "lion-roar-v187", "tiger": "tiger-roar", "tigerGrowl": "tiger-growl",
    "rooster": "rooster", "roosterFarm": "rooster-farm", "bird": "bird", "dog": "dog", "cat": "cat",
}
for destination, source in ANIMALS.items():
    shutil.copyfile(SOURCE / (source + ".mp3"), SOUNDS / (destination + ".mp3"))
for filename in ("credits.html", "sources-v186.json", "sources-v187.json"):
    shutil.copyfile(SOURCE / filename, ASSETS / filename)


class CreditText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.skip = True
        if tag in ("p", "li", "h1", "h2", "tr", "br"):
            self.parts.append("\n")
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href.startswith("http"):
                self.parts.append(" " + href + " ")

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.skip = False

    def handle_data(self, text):
        if not self.skip:
            self.parts.append(text)


credits = CreditText()
credits.feed((SOURCE / "credits.html").read_text())
(ASSETS / "credits.txt").write_text(
    "1560 알람 M · 동물 소리 출처\n\n"
    + re.sub(r"\n\s*\n\s*\n", "\n\n", "".join(credits.parts))
    + "\n\n기본 종·전자 알람·차임·버스 벨·사이렌·상승음: 이 앱에서 합성한 소리.\n"
)

RATE = 22050
for name in ("bell", "digital", "chime", "busbell", "siren", "rise"):
    samples = []
    for i in range(RATE * 3):
        t = i / RATE
        value = 0.0
        if name == "bell":
            for onset in (0, .65, 1.3):
                u = t - onset
                if 0 <= u < .6:
                    value += (math.sin(2*math.pi*880*u) + .35*math.sin(2*math.pi*1760*u)) * math.exp(-5*u) * min(1, u/.008)
        elif name == "digital":
            u = t % .6
            if t < 2.3 and u < .25:
                value = math.sin(2*math.pi*1050*t) * min(1, u/.008, (.25-u)/.008)
        elif name == "chime":
            for onset, frequency in ((0, 659.25), (.35, 830.61), (.7, 987.77), (1.05, 1318.51)):
                u = t - onset
                if 0 <= u < 1.3:
                    value += math.sin(2*math.pi*frequency*u) * math.exp(-3.5*u) * min(1, u/.01)
        elif name == "busbell":
            for onset, frequency in ((0, 880), (.65, 659.25), (1.3, 880), (1.95, 659.25)):
                u = t - onset
                if 0 <= u < .6:
                    value += math.sin(2*math.pi*frequency*u) * math.exp(-4*u) * min(1, u/.01)
        elif name == "siren":
            if t < 2.7:
                value = math.sin(2*math.pi*(650*t + 150/(2*math.pi)*(-math.cos(2*math.pi*t)+1))) * min(1, t/.02, (2.7-t)/.05)
        else:
            u = t % .7
            if t < 2.7 and u < .5:
                value = math.sin(2*math.pi*(650*u+550*u*u)) * min(1, u/.01, (.5-u)/.03)
        samples.append(value)
    peak = max(abs(value) for value in samples) or 1
    with wave.open(str(SOUNDS / (name + ".wav")), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(b"".join(struct.pack("<h", round(value/peak * .72 * 32767)) for value in samples))
print("Prepared 14 alarm sounds and their credits")
