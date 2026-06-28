---
name: filme
description: Transforma uma historia (historia.json do skill roteiro/contrato inemafilme.historia/v1) num FILME narrado e dinamico no pixflow — parallax 2.5D, sem IA de video. Gera as imagens (flux2-klein), aplica camera por emocao + efeitos + white-flash, renderiza, e monta o audio (narracao bella + Giuseppe, musica com build, SFX braam) com ducking. Use quando o usuario pedir "faz o filme", "transforma a historia/roteiro em video", "renderiza o filme", "vira filme essa historia", "monta o video do episodio", ou der uma historia.json/historia.md e quiser o MP4. NAO escreve a historia (isso e o skill `roteiro`); NAO usa gerador de video por IA.
---

# filme

`historia.json` → **filme narrado** no pixflow (parallax 2.5D determinístico). É o renderizador
do inemafilme: consome a história agnóstica (do skill `roteiro`) e a transforma em vídeo.
Direção de câmera/efeitos: ver `knowledge/direcao.md` (e o canônico `pixflow-trailer/inteligencia-direcao.md`).

## Pré-requisitos (sondar antes)
- `inemaimg` (flux2-klein) em `localhost:8000` — imagens.
- `pixflow-motion` instalado + deps (`node .../pixflow-motion.mjs check-deps`).
- `inemavox` bella em `:7860` (narração; sondar — pode oscilar) + `edge-tts` (Giuseppe + fallback).
- `inemavox2/baixar_v1.py` (yt-dlp) — música/SFX. `ffmpeg`.

## Fluxo
1. **Decupagem.** Copie `templates/decupagem.template.mjs` → `~/projetos/output/<id>/decupagem.mjs`.
   Para CADA beat da `historia.json`, preencha um objeto `{ key, look, emocao, caps, flash, imgs }`.
   **Expanda** a `cena.descricao_visual` de cada beat em **~8-12 prompts de plano** variados
   (wide / detalhe / personagem / ambiente / ação). A `emocao` (do beat) escolhe o pool de câmera e o ritmo.
   Quanto mais imagens, mais dinâmico — e **não encarece o render** (só a geração de imagem).
2. **Build.** `node decupagem.mjs` → gera as imagens (flux2-klein) + `<project>.movie.yaml` + `timeline.json`.
   Valide rápido antes com `node decupagem.mjs --no-img` (só yaml/timeline). Crie um placeholder de áudio:
   `ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t <dur+2> trilha.wav`.
3. **Render.** `node ~/.claude/skills/pixflow-motion/cli/pixflow-motion.mjs render <project>.movie.yaml <project>-mudo.mp4`
   (longo — rode em background; ≈ proporcional à duração: ~2-3 min de filme ≈ 30-50 min).
4. **Narração.** Copie `templates/narracao.template.py` → `narracao.py`, preencha `LINES` (bella + Giuseppe),
   cronometradas pelos `timeline.json → beatStart`. `python3 narracao.py` → `narracao.wav`.
5. **Música + SFX.** `scripts/baixar_musica.sh "<query cinematic build>" <dur>` → `music_bed.wav`.
   `python3 scripts/build_sfx.py --climax-beat <beat do climax> --hit-beats <beat de tensao>` → `sfx.wav`.
6. **Mux.** `scripts/mux.sh <project>` → mixa (música ducked + SFX + voz) e produz `<project>.mp4`
   (final) + `<project>-tg.mp4` (<50MB). Áudio é barato → itere por re-mux, sem re-render.
7. **Entrega.** MP4 em `~/projetos/output/<id>/`. Se o usuário pedir, envie no **openpcbot**
   (Telegram `sendVideo` com a versão `-tg.mp4`; token/chat em `~/projetos/openpcbot/.env`).

## Regras de direção (resumo — detalhe em knowledge/direcao.md)
- **Nunca plano estático**; planos curtos; muita troca de imagem; câmera variada por emoção.
- **medo/fúria** = cortes rápidos + `crash_zoom`/`whip_pan`/`dolly_zoom`; **lírico** = `crane`/`pull_out`/`ken_burns`.
- **white-flash** nos impactos do clímax (`flash:[...]`); `crossfade`/`dip_to_black` nas viradas de beat.
- **SFX é a alavanca de "ação"**: braam no clímax (pico alinhado), hits na tensão, whoosh nas transições.
- Música com **build** (calma→épica), **ducking** sob a voz.

## Roadmap
- v1 = só narrador (atual). v2 = falas de personagem (o contrato já tem `quem` por fala).
- Motor de IA de vídeo (SkyReels A2V / Wan) = upgrade futuro, plugável (ver `../FUTURO-MOTORES-IA-VIDEO.md`).

## Exemplo completo
`exemplo/avatar-eco-cinzas-v2/` — "Avatar — O Eco das Cinzas" (96 planos, bella+Giuseppe, SFX braam).
Referência canônica de trailer: `pixflow-trailer/examples/avatar-fogo-cinzas/` (78 shots).
