# Direção do `filme` — câmera, looks, efeitos, ritmo

O motor (`scripts/engine.mjs`) já aplica a maior parte disto automaticamente a partir da
**emoção de cada beat**. Este doc é a referência do que existe e como a gente usa.
Catálogo canônico profundo (verbo de cinema → primitivo): `pixflow-trailer/inteligencia-direcao.md`.
Implementação: `pixflow/skill/src/camera.js` (18 câmeras) e `src/looks.js` (6 looks).

## Princípio nº 1 (o que matou a v1)
Sem IA de vídeo, o dinamismo vem de **(a) movimento em TODO plano** (nunca `static`),
**(b) alta troca de imagem** (planos curtos, muitas imagens) e **(c) SFX + música com build**.
**4x mais imagens NÃO encarece o render** (render escala com a DURAÇÃO, não com o nº de cortes) —
só custa geração de imagem. Então seja generoso no nº de planos.

## Os 18 movimentos de câmera (pixflow)
`static` (evite), `push_in` (close emocional), `pull_out` (revela contexto), `crash_zoom`
(zoom acelerado = impacto), `ken_burns` (foto viva), `pan`/`tilt` (varre horiz/vert),
`pedestal` (sobe/desce a moldura), `tracking`/`truck` (acompanha lateral, parallax++),
`dolly` (translada+zoom, profundidade), `crane` (sobe revelando escala), `aerial` (drone, vastidão),
`orbit` (gira ao redor), `float` (flutua, sonho), `handheld` (mão, ação/urgência),
`dolly_zoom` (vertigo Hitchcock), `whip_pan` (chicote borrado, transição veloz), `framing` (viaja A→B).
- **1 movimento por cena** (somar dois estoura o zoom → bordas pretas).
- params: `intensity`, `amplitude` (`sutil`/`normal`/`dramatico`), `direction`, `easing`.

## Pools por emoção (o que o engine faz)
| emoção (historia) | energia | câmeras | ritmo |
|---|---|---|---|
| tensao | tense | dolly, whip_pan, push_in, tracking, handheld, pan | ~1.6s |
| misterio | myst | push_in, float, pull_out, ken_burns, orbit, tilt | ~1.8s |
| medo | fear | handheld, crash_zoom, whip_pan, dolly, tilt | ~1.4s (rápido) |
| melancolia | melan | pull_out, ken_burns, crane, float, pedestal | ~2.1s (lento) |
| ternura | tender | push_in, ken_burns, float, pedestal | ~2.1s |
| euforia/furia | fury | crash_zoom, dolly_zoom, whip_pan, handheld, push_in | ~1.05s (cortes secos) |
| esperanca | hope | aerial, crane, pull_out, push_in, ken_burns | ~1.9s |

## Looks (6) e o que cada um liga
- `cinema-dramatico` — grain+vignette+chroma+bloom (emoção, rosto, íntimo)
- `sci-fi-cyberpunk` — vignette alta+chroma forte+bloom (tech, frio, dissolução/glitch)
- `noir-film` — grain+vignette alta (sóbrio, cartela, mundo morto)
- `retro-vhs` — grain+chroma alto (flashback)
- `sonho-etereo` — bloom+saturação (maravilha, lírico, payoff)
- `acao-epico` — grain baixo+chroma+bloom (batalha, clímax)

## Transições
`cut` (padrão, ritmo de trailer), `crossfade` (0.5–0.6s, respiro/beleza),
`dip_to_black` (0.4–0.7s, quebra de seção). O engine: `cut` no miolo do beat, `crossfade`/`dip`
no fim de cada beat, e **white-flash** (`kind:'white'`, 0.1s) nos impactos do clímax (`flash:[...]`).

## Áudio (camadas)
- **narração:** bella (:7860, principal) + Giuseppe (edge-tts it-IT, épico em abertura/clímax/final). `templates/narracao.template.py`.
- **música:** royalty-free via inemavox, com build calma→épica. `scripts/baixar_musica.sh`.
- **SFX:** braam no clímax (pico alinhado) + hits; whoosh em transições; explosão+vocal em batalha. `scripts/build_sfx.py`.
- **mix:** música com **ducking** (sidechain) sob a voz; SFX por cima. `scripts/mux.sh`.
- Imagem/render é caro; **áudio é barato** → itere narração/mix por re-mux, sem re-render.

## Modelos de referência (filmes completos prontos)
- `pixflow-trailer/examples/avatar-fogo-cinzas/` — decupagem de 78 shots + build (TODAS as câmeras/looks). Canônico.
- `~/projetos/output/avatar-eco-cinzas-v2/` — gerador programático, 96 planos, bella+Giuseppe, SFX braam. Padrão deste skill.
- `pixflow/examples/demo.movie.yaml` — mínimo (2 cenas).
