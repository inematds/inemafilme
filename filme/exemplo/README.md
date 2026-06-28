# Exemplos — modelos de filme completos

## `avatar-eco-cinzas-v2/` (padrão deste skill)
"Avatar — O Eco das Cinzas" — 96 planos, 2:48, 1280×720.
- `historia.json` — a história (saída do skill `roteiro`).
- `build.mjs` — a decupagem (predecessora self-contained do `templates/decupagem.template.mjs`):
  9 beats → ~91 imagens, gerador programático com pools de câmera por emoção, white-flash no clímax.
- `narra2.py` — narração **bella + Giuseppe** (épico na abertura/clímax/final), cronometrada nos beats.
- `build_sfx.py` — SFX braam com pico alinhado no clímax + hit ao entrar nas Cinzas.
- MP4 final + WAVs ficam em `~/projetos/output/avatar-eco-cinzas-v2/` (não versionados aqui).

> `build.mjs` aqui é a versão self-contained que deu origem ao `engine.mjs` + templates.
> Para um filme NOVO, use `templates/decupagem.template.mjs` (importa o `engine.mjs`).

## Outras referências (no ecossistema, não copiadas)
- `pixflow-trailer/examples/avatar-fogo-cinzas/` — **canônico**: decupagem de 78 shots + build com
  todas as 18 câmeras / 6 looks / cartelas / áudio. A melhor referência de "como ver cinema → shots".
- `pixflow/examples/demo.movie.yaml` — mínimo (2 cenas).
- `pixflow-trailer/inteligencia-direcao.md` — a receita canônica verbo-de-cinema → primitivo.
