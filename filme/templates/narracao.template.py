#!/usr/bin/env python3
"""NARRAÇÃO — copie p/ o diretorio do projeto, preencha LINES, rode: python3 narracao.py
Gera narracao.wav cronometrada nos beats. Vozes:
  - 'bella'    -> inemavox :7860 (voz default do Nei, intima) — SONDAR antes (pode oscilar)
  - 'giuseppe' -> edge-tts it-IT-GiuseppeMultilingualNeural (grave/epico) p/ abertura, climax, frase final
Pegue os tempos de inicio de cada beat em timeline.json -> beatStart (gerado pela decupagem)."""
import urllib.request, json, subprocess, os
os.makedirs("voz", exist_ok=True)
BELLA = "http://127.0.0.1:7860/tts/vc"

def bella(text, out):
    data = json.dumps({"text": text, "voice": "bella", "lang": "pt", "bitrate": "128k"}).encode()
    req = urllib.request.Request(BELLA, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r, open(out, "wb") as f:
        f.write(r.read())

def giuseppe(text, out):
    subprocess.run(["edge-tts", "--voice", "it-IT-GiuseppeMultilingualNeural",
                    "--rate=-8%", "--pitch=-6Hz", "--text", text, "--write-media", out], check=True)

TOTAL = 169  # ajuste p/ timeline.totalSec + 1

# (start_s, voz, texto) — falas curtas e dramáticas, ~1-2 por beat, dentro da janela de cada beat.
LINES = [
    # (2.5,   "giuseppe", "Abertura épica..."),
    # (18.0,  "bella",    "Fala principal..."),
]

mp3s = []
for i, (t, v, txt) in enumerate(LINES):
    out = f"voz/l{i:02d}.mp3"
    (bella if v == "bella" else giuseppe)(txt, out)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of", "default=nw=1:nk=1", out]).strip())
    mp3s.append((t, out, dur))
    flag = "  <-- OVERLAP" if i + 1 < len(LINES) and t + dur > LINES[i + 1][0] + 0.3 else ""
    print(f"  l{i:02d} {v:8} t={t:6.1f} dur={dur:4.1f} end={t+dur:6.1f}{flag}")

inputs, filt = [], []
for i, (t, out, dur) in enumerate(mp3s):
    inputs += ["-i", out]
    filt.append(f"[{i}:a]adelay={int(t*1000)}|{int(t*1000)}[a{i}]")
mix = "".join(f"[a{i}]" for i in range(len(mp3s))) + f"amix=inputs={len(mp3s)}:dropout_transition=0:normalize=0[m]"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
                ";".join(filt) + ";" + mix, "-map", "[m]", "-t", str(TOTAL), "-ar", "44100", "-ac", "2", "narracao.wav"], check=True)
print("narracao.wav ok")
