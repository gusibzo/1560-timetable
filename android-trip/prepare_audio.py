"""Build offline PCM alerts matching the 1560 timetable."""
from array import array
from math import exp, pi, sin
from pathlib import Path
import subprocess
import sys
import wave

RATE = 24000
SOURCE = Path(__file__).resolve().parent.parent / "audio" / "trip"
out = Path(sys.argv[1])

def voice(name):
    return subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(SOURCE / name), "-f", "s16le",
        "-ar", str(RATE), "-ac", "1", "-"
    ])

def chime(notes, repeat):
    samples = [0.0] * int(((repeat - 1) * 1.45 + (len(notes) - 1) * .27 + notes[-1][1]) * RATE + 1)
    for group in range(repeat):
        for index, (frequency, duration) in enumerate(notes):
            start = int((group * 1.45 + index * .27) * RATE)
            for step in range(int(duration * RATE)):
                seconds = step / RATE
                envelope = min(seconds / .015, 1) * exp(-5 * seconds / duration)
                samples[start + step] += sin(2 * pi * frequency * seconds) * envelope * 14000
    return array("h", (max(-32768, min(32767, int(sample))) for sample in samples)).tobytes()

departure = chime([(1046.50, .28), (783.99, .42)], 1)
arrival = chime([(1318.51, .32), (1046.50, .32), (783.99, .56)], 3)
gap = bytes(RATE * 2 // 6)
gate = voice("kyung-hee-gate-ko.mp3")
for name, data in (
    ("departure", departure + gap + voice("departure-ko.mp3")),
    ("arrival", arrival), ("gate", arrival + gap + gate), ("gate_voice", gate),
):
    with wave.open(str(out / ("trip_" + name + ".wav")), "wb") as output:
        output.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        output.writeframes(data)
