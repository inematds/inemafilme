#!/usr/bin/env python3
"""SFX -> sfx.wav. Baixa um braam (se faltar), acha o pico e crava o impacto no clímax (+ hits extras).
Uso (no diretorio do projeto, com timeline.json presente):
  python3 .../filme/scripts/build_sfx.py --climax-beat b8 --hit-beats b6
  python3 .../filme/scripts/build_sfx.py --climax-sec 130.2 --hit-secs 88.7
Lê os tempos dos beats de timeline.json -> beatStart. Requer ffmpeg, yt-dlp (via inemavox)."""
import argparse, json, subprocess, wave, array, os, sys

BAIXAR = "/home/nmaldaner/projetos/inemavox2/baixar_v1.py"
ap = argparse.ArgumentParser()
ap.add_argument("--climax-beat"); ap.add_argument("--climax-sec", type=float)
ap.add_argument("--hit-beats", default=""); ap.add_argument("--hit-secs", default="")
ap.add_argument("--query", default="cinematic braam riser impact sound effect")
a = ap.parse_args()

tl = json.load(open("timeline.json"))
bs = tl.get("beatStart", {}); total = tl.get("totalSec", 169)
climax = a.climax_sec if a.climax_sec is not None else bs.get(a.climax_beat)
if climax is None:
    sys.exit("informe --climax-sec ou --climax-beat valido (existente em timeline.beatStart)")
hits = [float(x) for x in a.hit_secs.split(",") if x] + [bs[b] for b in a.hit_beats.split(",") if b and b in bs]

# garante o braam
if not os.path.exists("sfx_braam/video.mp4"):
    subprocess.run(["python3", BAIXAR, "--url", f"ytsearch1:{a.query}", "--outdir", "sfx_braam"], check=True)

# acha o pico (janela de 50ms de maior amplitude)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "sfx_braam/video.mp4", "-vn", "-ac", "1", "-ar", "44100", "braam_mono.wav"], check=True)
w = wave.open("braam_mono.wav", "rb"); fr = w.getframerate()
arr = array.array("h"); arr.frombytes(w.readframes(w.getnframes())); w.close()
win = int(0.05 * fr); best = 0; peak = 0.0
for i in range(0, len(arr) - win, win):
    s = max(abs(x) for x in arr[i:i + win])
    if s > best:
        best = s; peak = i / fr
print(f"braam peak ~ {peak:.2f}s -> impacto no climax {climax}s")

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "sfx_braam/video.mp4", "-vn", "-ac", "2", "-ar", "44100", "-af", "loudnorm=I=-14", "braam.wav"], check=True)

# monta: braam forte no climax + braams mais baixos nos hits
parts = [(climax, 1.0)] + [(h, 0.45) for h in hits]
inputs, filt, labels = [], [], []
for i, (t, vol) in enumerate(parts):
    d = max(0, int((t - peak) * 1000))
    inputs += ["-i", "braam.wav"]
    filt.append(f"[{i}:a]adelay={d}|{d},volume={vol}[s{i}]"); labels.append(f"[s{i}]")
fc = ";".join(filt) + ";" + "".join(labels) + f"amix=inputs={len(parts)}:dropout_transition=0:normalize=0[m]"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[m]", "-t", str(int(total) + 1), "-ar", "44100", "-ac", "2", "sfx.wav"], check=True)
print(f"sfx.wav ok ({len(parts)} hits)")
