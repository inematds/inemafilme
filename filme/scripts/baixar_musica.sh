#!/usr/bin/env bash
# Baixa uma trilha royalty-free (inemavox/yt-dlp) e extrai music_bed.wav com fade in/out.
# Uso (no diretorio do projeto):  baixar_musica.sh "<query>" <duracao_s>
# Ex.: baixar_musica.sh "epic emotional cinematic orchestral building no copyright music" 169
set -euo pipefail
Q="${1:?uso: baixar_musica.sh \"query\" <dur_s>}"; D="${2:?informe a duracao em segundos}"
python3 /home/nmaldaner/projetos/inemavox2/baixar_v1.py --url "ytsearch1:${Q}" --outdir music
OUT=$(ls -t music/*.mp4 music/*.m4a music/*.webm 2>/dev/null | head -1)
[ -n "$OUT" ] || { echo "download falhou"; exit 1; }
FADE_OUT=$((D - 4))
ffmpeg -y -loglevel error -i "$OUT" -t "$D" -vn -ac 2 -ar 44100 \
  -af "afade=t=in:st=0:d=3,afade=t=out:st=${FADE_OUT}:d=4,loudnorm=I=-20" music_bed.wav
echo "music_bed.wav ok (${D}s) <- $OUT"
