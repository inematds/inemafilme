#!/usr/bin/env bash
# Mix final (musica ducked sob a voz + SFX + narracao) + mux no video + versao leve p/ Telegram.
# Uso (no diretorio do projeto):  mux.sh <project>
#   espera: <project>-mudo.mp4 (render do pixflow), music_bed.wav, narracao.wav, sfx.wav (sfx opcional)
#   produz: <project>.mp4 (final) + <project>-tg.mp4 (<50MB)
set -euo pipefail
P="${1:?uso: mux.sh <project>}"
[ -f "${P}-mudo.mp4" ] || { echo "falta ${P}-mudo.mp4 (render)"; exit 1; }
[ -f narracao.wav ] || { echo "falta narracao.wav"; exit 1; }
[ -f music_bed.wav ] || { echo "falta music_bed.wav"; exit 1; }
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "${P}-mudo.mp4" | cut -d. -f1)
T=$((DUR + 1))

if [ -f sfx.wav ]; then
  ffmpeg -y -loglevel error -i music_bed.wav -i narracao.wav -i sfx.wav -filter_complex "
    [1:a]volume=1.5,asplit=2[sc][voice];
    [0:a][sc]sidechaincompress=threshold=0.04:ratio=8:attack=15:release=400[dm];
    [2:a]volume=0.7[sfx];
    [dm][sfx]amix=inputs=2:duration=longest:normalize=0[bed];
    [bed][voice]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-15:TP=-1.5[out]" \
    -map "[out]" -t "$T" final_audio.wav
else
  ffmpeg -y -loglevel error -i music_bed.wav -i narracao.wav -filter_complex "
    [1:a]volume=1.5,asplit=2[sc][voice];
    [0:a][sc]sidechaincompress=threshold=0.04:ratio=8:attack=15:release=400[dm];
    [dm][voice]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-15:TP=-1.5[out]" \
    -map "[out]" -t "$T" final_audio.wav
fi
echo "final_audio.wav ok"

# mux preservando a duracao do video (pad do audio)
ffmpeg -y -loglevel error -i "${P}-mudo.mp4" -i final_audio.wav \
  -filter_complex "[1:a]apad[a]" -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "${P}.mp4"
echo "${P}.mp4 ok"

# versao Telegram (<50MB)
ffmpeg -y -loglevel error -i "${P}.mp4" -c:v libx264 -preset veryfast -crf 30 -c:a aac -b:a 128k -movflags +faststart "${P}-tg.mp4"
echo "${P}-tg.mp4 ok ($(du -m "${P}-tg.mp4" | cut -f1)MB)"
