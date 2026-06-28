// DECUPAGEM do filme — copie p/ ~/projetos/output/<id>/ , preencha BEATS a partir da historia.json,
// e rode:  node decupagem.mjs        (gera imagens + .movie.yaml + timeline.json)
//          node decupagem.mjs --no-img   (só reescreve yaml/timeline)
// A inteligência de câmera/efeitos (pools por emoção, white-flash, transições) mora no engine.
// Catálogo de movimentos/looks: ../../inemafilme/filme/knowledge/direcao.md
import { montarFilme } from '/home/nmaldaner/.claude/skills/filme/scripts/engine.mjs';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = dirname(fileURLToPath(import.meta.url));
const NOIMG = process.argv.includes('--no-img');

// 1 objeto por beat da historia.json (mesma ordem). Campos:
//   key:    'b1','b2',...  (vira id dos planos: b1_00, b1_01...)
//   emocao: a do beat na historia (tensao|misterio|medo|melancolia|ternura|euforia|furia|esperanca)
//           -> define o POOL de câmera e o ritmo (medo/fúria = cortes rápidos + crash_zoom/whip_pan)
//   look:   noir-film | sci-fi-cyberpunk | cinema-dramatico | sonho-etereo | acao-epico | retro-vhs
//   imgs:   ~8-12 PROMPTS de plano. EXPANDA a cena.descricao_visual em ângulos variados
//           (wide estabelecendo, detalhe/close, personagem, ambiente, movimento/ação). Quanto mais
//           imagens, mais dinâmico (NÃO encarece o render — só a geração de imagem).
//   caps:   { 8: 'legenda na tela' }  -> usa as falas/linhas-chave da historia (opcional)
//   flash:  [1,4,8]  -> insere white-flash de impacto APÓS esses planos (só no clímax)
const BEATS = [
  { key: 'b1', look: 'noir-film', emocao: 'tensao', caps: {}, imgs: [
    'PREENCHER: plano wide estabelecendo o cenário do beat 1',
    'PREENCHER: detalhe / close do elemento central',
    'PREENCHER: mais um ângulo (ambiente / personagem / movimento)',
  ] },
  // { key: 'b2', look: 'sonho-etereo', emocao: 'misterio', caps: { 8: 'fala-chave.' }, imgs: [ ... ] },
  // ... um por beat, até o último (payoff) ...
];

await montarFilme(BEATS, {
  root: ROOT,
  project: 'meu-filme',          // vira meu-filme.movie.yaml e o nome do mp4
  title: 'TÍTULO DO FILME',
  kicker: 'subtítulo',
  // ajuste o STYLE ao universo da historia (mantenha 'no text' e a separação FG/MG/BG p/ parallax):
  style: 'cinematic, hyperrealistic, epic dramatic volumetric lighting, vibrant colors, high detail, film grain, shallow depth of field, strong foreground / midground / deep background separation for parallax, dynamic composition, no text',
  width: 1280, height: 720, fps: 30,   // 9:16 = 720x1280
  noImg: NOIMG,
});
