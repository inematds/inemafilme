#!/usr/bin/env python3
"""Narracao v2: bella (:7860, principal) + Giuseppe (edge-tts it-IT, epico) -> narracao.wav."""
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

# (start_s, voz, texto)
LINES = [
    (2.5,   "giuseppe", "Pandora sobreviveu aos homens. Mas ficou com uma ferida que nunca fechou."),
    (9.8,   "bella",    "As Cinzas. O único lugar onde Eywa ficou surda."),
    (18.0,  "bella",    "Rini nasceu marcada. E ouve o que ninguém mais ouve."),
    (26.5,  "bella",    "Um sussurro vindo da zona morta. Todos diziam que era loucura."),
    (35.0,  "bella",    "Seu amigo entrou nas Cinzas. E voltou vazio."),
    (42.5,  "bella",    "A morte começou a avançar. E ninguém sabia o porquê."),
    (50.2,  "bella",    "A anciã revelou: para vencer a guerra, Eywa cortou um galho de si mesma."),
    (61.0,  "bella",    "E o que foi esquecido nunca perdoou."),
    (72.0,  "bella",    "Antes de partir, a anciã lhe deu um fio do próprio cabelo."),
    (80.5,  "bella",    "Para que ela não esquecesse quem era."),
    (89.4,  "bella",    "Dentro das Cinzas, o silêncio devorava as lembranças."),
    (99.5,  "bella",    "A cada passo, Rini esquecia mais. Até o próprio nome."),
    (110.2, "bella",    "No coração da zona morta não havia um monstro."),
    (118.5, "bella",    "Havia alguém esquecido. Que só queria não estar só."),
    (130.8, "giuseppe", "Quando o esquecimento quase a tomou, ela lembrou quem era!"),
    (138.0, "giuseppe", "E fez o impensável: em vez de fugir, ela o ouviu."),
    (146.2, "bella",    "As Cinzas voltaram a sussurrar. Agora, em coro."),
    (154.0, "bella",    "Onde só houve silêncio, nasceu uma folha verde."),
    (160.5, "giuseppe", "A marca não era maldição. Era uma ponte."),
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
                ";".join(filt) + ";" + mix, "-map", "[m]", "-t", "169", "-ar", "44100", "-ac", "2", "narracao.wav"], check=True)
print("narracao.wav ok")
