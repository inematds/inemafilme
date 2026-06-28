#!/usr/bin/env python3
"""Acha o pico do braam e monta sfx.wav (169s): impacto no climax + hit ao entrar nas Cinzas."""
import subprocess, wave, array

# extrai braam mono p/ achar o pico
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "sfx_braam/video.mp4",
                "-vn", "-ac", "1", "-ar", "44100", "braam_mono.wav"], check=True)
w = wave.open("braam_mono.wav", "rb"); fr = w.getframerate()
a = array.array("h"); a.frombytes(w.readframes(w.getnframes())); w.close()
win = int(0.05 * fr); best = 0; peak = 0.0
for i in range(0, len(a) - win, win):
    s = max(abs(x) for x in a[i:i + win])
    if s > best:
        best = s; peak = i / fr
print(f"braam peak ~ {peak:.2f}s")

# braam estereo normalizado
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "sfx_braam/video.mp4",
                "-vn", "-ac", "2", "-ar", "44100", "-af", "loudnorm=I=-14", "braam.wav"], check=True)

CLIMAX = 130.2   # b8 start
ASHES = 88.7     # b6 start (entra nas Cinzas)
d_climax = max(0, int((CLIMAX - peak) * 1000))
d_ashes = max(0, int((ASHES - peak) * 1000))

# sfx: braam forte no climax + braam mais baixo nas Cinzas
fc = (f"[0:a]adelay={d_climax}|{d_climax},volume=1.0[c];"
      f"[1:a]adelay={d_ashes}|{d_ashes},volume=0.45[a];"
      f"[c][a]amix=inputs=2:dropout_transition=0:normalize=0[m]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "braam.wav", "-i", "braam.wav",
                "-filter_complex", fc, "-map", "[m]", "-t", "169", "-ar", "44100", "-ac", "2", "sfx.wav"], check=True)
print(f"sfx.wav ok (climax@{CLIMAX}s adelay={d_climax}ms, cinzas@{ASHES}s)")
