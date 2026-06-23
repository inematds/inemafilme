# inemafilme — Design

> Documento de design. Status: **rascunho para aprovação**. Data: 2026-06-23.
> Próximo passo após aprovação: plano de implementação (skill `writing-plans`).

## 1. Visão geral

`inemafilme` gera um **filme/episódio narrado** que conta uma história inteira,
estilo inemaref, usando o motor de cinema do pixflow (parallax 2.5D
determinístico, **sem IA de vídeo**). A entrada é flexível:

- Você passa um **roteiro** → ele usa.
- Você não passa → ele **inventa a história**.
- Você passa **referências/imagens** → ele usa; senão **gera** (como o inemaref).

O sistema é dividido em **três peças** com responsabilidades isoladas. A peça
central — o `story-engine` — é a "máquina de história": pensa retenção e
narrativa, e **não sabe nada de render**. Isso a torna reutilizável (o inemaref
poderá chamá-la no futuro) e mantém o renderizador burro e trocável.

## 2. Escopo: três peças + roadmap

| Peça | Responsabilidade | Sabe de render? |
|------|------------------|-----------------|
| **contrato `historia`** | O formato neutro que liga tudo (a "junta") | — |
| **`story-engine`** (skill) | assunto/roteiro → `historia.md` + `historia.json`, com engenharia de retenção | **Não** |
| **`filme`** (skill) | `historia.json` → filme narrado no pixflow | Sim (pixflow) |

**Roadmap de versões:**

- **v1 (foco agora):** só **narrador** conta a história. ~5 min, **planos curtos
  e troca constante** (~100–150 planos, com **reuso de imagem** pra segurar o
  custo), filme único fechado, motor **pixflow** (barato). Voz `bella` (inemavox).
- **v2:** entram **falas de personagem** (cada personagem com sua voz). O
  contrato já está pronto pra isso (ver §3).
- **v3:** **episódios recorrentes** do mesmo mundo + integração com o
  `inemaref-serie` (reuso de bíblia/personagens), e renderizadores extras
  plugáveis (HQ do inemaref; IA de vídeo — ver §8).

## 3. O contrato `historia` (a peça mais importante)

Formato **híbrido**, derivado e validado pelo `story.md` do `animabook`
(`animabook/src/lib/parseStory.ts`), estendido com metadados narrativos:

- **Camada humana — `historia.md`**: legível, editável à mão, versionável.
- **Camada de máquina — `historia.json`**: compilada do `.md`, consumida pelos
  renderizadores.

A regra de ouro: **toda fala carrega um campo `quem`** (`narrador` na v1; na v2
abre pra `jake`, `neytiri`...). Essa é a ponte v1→v2 — adicionar vozes de
personagem não exige reengenharia. E a **cena é descrita, não dirigida**: o
`story-engine` diz *o que se vê e a emoção*; o `filme` decide câmera/look/prompt.
Assim o mesmo `historia.json` pode ser renderizado por pixflow hoje, por HQ do
inemaref, ou por IA de vídeo amanhã.

### 3.1 `historia.md` (exemplo)

```markdown
---
id: avatar-ep01
titulo: "Avatar — A Chama e as Cinzas"
logline: "Um fuzileiro paralítico ganha um corpo alienígena e precisa escolher entre dois mundos."
promessa_central: "Jake vai abandonar os humanos pelos Na'vi — e a que preço?"
duracao_alvo_s: 300
formato: "16:9"
voz_narrador: bella
look_padrao: cinema-dramatico
---

## ato1 :: gancho
<!-- beat: gancho | retencao: cold_open | emocao: tensao | tempo_s: 8 -->
<!-- loop: abre=mundo-perigoso -->
<!-- cena: nave humana cruzando o vazio em direção a um gigante gasoso azul; ambiente: orbita de Pandora; personagens: -->
> Em 2154, a Terra está morta. O que sobrou da humanidade busca um tesouro a anos-luz de casa.

## ato1 :: protagonista
<!-- beat: apresenta_protagonista | retencao: promessa | emocao: melancolia | tempo_s: 12 -->
<!-- loop: abre=promessa-central -->
<!-- cena: ex-fuzileiro em cadeira de rodas olhando a chuva pela janela de um quarto apertado; ambiente: cidade decadente; personagens: jake -->
> Jake Sully perdeu as pernas numa guerra que já esqueceu o nome. Mas ainda sabe lutar.
[Jake]: Eu só queria uma razão pra continuar.   <!-- v2: ignorado na v1 -->
```

### 3.2 `historia.json` (schema)

```jsonc
{
  "versao_contrato": "inemafilme.historia/v1",
  "id": "avatar-ep01",
  "titulo": "...",
  "logline": "...",
  "promessa_central": "a pergunta dramatica que segura o filme ate o fim",
  "duracao_alvo_s": 300,
  "formato": "16:9",            // ou "9:16"
  "voz_narrador": "bella",
  "look_padrao": "cinema-dramatico",
  "personagens": [              // elenco; alimenta consistência visual (§6)
    { "nome": "jake", "aparencia": "ex-fuzileiro, ~30 anos, cabelo raspado, cicatriz..." }
  ],
  "beats": [
    {
      "id": "b01",
      "ato": 1,
      "ordem": 1,
      "funcao_retencao": "cold_open",   // cold_open|promessa|escalada|virada|climax|respiro|payoff|gancho_proximo
      "emocao": "tensao",               // tensao|medo|melancolia|esperanca|euforia|misterio|ternura|furia
      "tempo_s": 8,
      "loop": { "abre": ["promessa-central"], "fecha": [] },  // listas: um beat pode abrir/fechar varios loops
      "falas": [
        { "quem": "narrador", "texto": "Em 2154, a Terra está morta..." }
      ],
      "cena": {
        "descricao_visual": "nave humana cruzando o vazio rumo a um gigante gasoso azul",
        "ambiente": "orbita de Pandora",
        "personagens_em_cena": [],
        "look_sugerido": "sci-fi-cyberpunk"   // dica opcional; o filme pode sobrepor
      }
    }
  ]
}
```

**Campos que o animabook NÃO tinha e o `story-engine` adiciona:**
`promessa_central`, `funcao_retencao`, `emocao`, `tempo_s`, `quem` por fala,
`loop` (abre/fecha), `personagens` (elenco), e o cabeçalho narrativo.

### 3.3 O motor de retenção: a promessa e os loops

O que faz alguém continuar assistindo não é "o que está acontecendo", é **o que
ainda não aconteceu** — a pessoa fica porque foi *prometido* que algo vem. Esse é
o coração do `story-engine`, não um detalhe:

- **Promessa central (`promessa_central`):** uma única **pergunta dramática**
  plantada nos primeiros segundos e respondida só no fim ("Jake vai abandonar os
  humanos pelos Na'vi — e a que preço?"). O filme inteiro é a resposta adiada.
- **Loops aninhados (`loop.abre` / `loop.fecha`):** cada beat **abre** uma
  perguntinha e/ou **fecha** uma anterior. Regra de ferro: **nunca deixar um
  trecho sem nenhum loop aberto** — sempre tem algo no ar. Fecha-se um loop
  pequeno, mas a promessa central segue aberta.
- **Setup → payoff:** planta-se cedo (uma arma, uma frase, um objeto), paga-se
  tarde. Todo loop aberto tem que fechar (ou virar gancho deliberado).
- **Escalada:** a cada ato o custo sobe — a pergunta fica mais cara de responder.
- **Curiosity gap:** o espectador sabe algo que o personagem não sabe (ou
  vice-versa) — tensão de informação.

**"Por que ver o próximo capítulo?"** (recorrência, v3): o episódio **não fecha
tudo** — paga o loop pequeno do episódio, mas **abre um loop maior**
(`gancho_proximo`) antes dos créditos. No filme único (v1), o equivalente é
manter a promessa central aberta até o `payoff` final.

Isso é **mecanicamente verificado** pelo validador (§4): sem promessa, com
"deserto" sem loop aberto, ou com a promessa fechada cedo demais → reprova.

## 4. `story-engine` (sub-projeto 1 — o foco da v1)

**Responsabilidade única:** transformar *assunto OU roteiro* em uma `historia`
estruturada para reter atenção. Não renderiza nada.

**Modos de entrada:**

- **A — só assunto** (ex.: "a história do Avatar"): **inventa** a história
  completa (logline → arco de 3 atos → beats), aplicando retenção.
- **B — roteiro pronto** (texto/tratamento): **não inventa enredo**; segmenta em
  beats e injeta a estrutura de retenção (gancho, escalada, payoff), cortando
  gordura.
- **C — referências**: aparência de personagem/ambiente passada → usa; senão o
  campo fica como descrição e o `filme` gera (como o `inemaref-folder`).

**Como a "inteligência" funciona (padrão do ecossistema):** o trabalho criativo
(escrever a história) é feito pelo **agente seguindo o `SKILL.md` + a base de
conhecimento**, emitindo o `historia.md` — exatamente como o `inemaref-serie`
escreve `biblia.json`. Os **scripts** fazem só a parte determinística.

**Componentes:**

- `SKILL.md` — instruções + a gramática de retenção (quando abrir/fechar loop,
  como escalar tensão, ganchos para história longa narrada).
- `knowledge/` — **colhido** do que já existe: frameworks do `video-plan-editor`
  (Save the Cat, Jornada do Herói, hooks, loops) **recalibrados para história
  longa**, + as "três regras de conteúdo" do `inemaref-serie` (objetivo+
  contribuição, canon visual, narração fluente).
- `compilar.py` — `historia.md` → `historia.json` (parser estilo
  `parseStory.ts`, estendido com os metadados de beat).
- `validar.py` — valida schema + **checklist de retenção** (§3.3): existe
  `promessa_central` e um beat que a planta no ato 1? a promessa só fecha no
  `payoff` (não antes)? todo trecho tem ao menos um loop aberto (sem "deserto")?
  todo `loop.abre` é fechado (ou vira `gancho_proximo` deliberado)? há escalada?
  a soma de `tempo_s` bate com `duracao_alvo_s`? o nº de planos respeita o teto
  de custo (`max_planos`)?

**Saída:** `historia.md` + `historia.json` (+ relatório do validador).

## 5. `filme` (sub-projeto 2 — spec próprio depois; esboço aqui)

**Responsabilidade:** `historia.json` → MP4 narrado no pixflow. Reusa a
**inteligência de direção** do `pixflow-trailer`
(`pixflow/skill-trailer/inteligencia-direcao.md`).

**Fluxo (v1):**

1. **Direção:** cada beat → um (ou poucos) **planos**. Mapeia
   `cena.descricao_visual` + `emocao` + `funcao_retencao` → primitivo de câmera
   (push_in, ken_burns, dolly...), `look` e **prompt flux** otimizado;
   `duration` vem de `tempo_s`; transição vem da emoção/virada.
2. **Imagens:** flux2-klein via `inemaimg` (`localhost:8000`).
3. **Movie spec:** monta `*.movie.yaml` (pixflow.movie/v1) + `timeline.json`.
4. **Render:** `pixflow-motion` → MP4 mudo.
5. **Narração:** para cada `fala` com `quem == narrador` (v1), TTS `inemavox`
   `bella` (`127.0.0.1:7860`); ducking da música sob a voz.
6. **Música/SFX (v1 — central, não opcional):** trilha + ambiência + SFX via
   baixador do `inemavox` (royalty-free), com **ducking** sob a narração.
7. **Saída:** MP4 em `~/projetos/output/<id>/`.

### 5.1 Princípio de direção v1: movimento + troca constante

Como **não temos vídeo generativo** (nada de movimento real de footage), a
sensação de dinamismo vem de duas alavancas, que são **prioridade de direção** na
v1:

1. **Movimento em todo plano** — nunca um quadro parado. Toda cena ganha câmera
   ativa (push/dolly/pan/parallax forte); `static` é proibido por padrão.
2. **Alta troca de imagem** — planos **curtos** e troca **frequente**, pra o olho
   sempre ter algo novo. Isso puxa o `tempo_s` médio pra baixo (≈ 2–3 s) e o nº
   de planos pra cima.

**Custo vs. movimento (a sacada):** mais planos = mais imagens = mais caro. Pra
ter "muita movimentação" sem estourar a geração de imagem, o `filme` **reusa a
mesma imagem em 2+ planos com movimentos/recortes de câmera diferentes** (o
`pixflow-trailer` já tem o campo `reuse`): uma imagem gerada vira vários planos
distintos. Turnover alto, custo controlado.

**Na v2**, o passo 5 lê também `quem != narrador` → vozes por personagem; e
um plano de personagem falando pode ser roteado pra outro renderizador (§8).

## 6. Consistência de personagem

Calcanhar de Aquiles de gerar ~80 imagens. Estratégia (reusa o que o inemaref já
resolve): cada personagem do elenco vira um **`referencia.json` travado** (via
`inemaref-folder`), e os prompts de cena dos planos com aquele personagem
herdam a descrição travada. O `filme` injeta a referência nos prompts flux.

## 7. Decisões travadas

- Motor v1 = **pixflow** (barato, determinístico, sem IA de vídeo). ✔ confirmado.
- Duração v1 ≈ **5 min** (parametrizável: curto ~3 / médio ~5 / longo ~8).
- v1 = **filme único fechado**; recorrência fica pra v3.
- v1 = **só narrador**; áudio modelado como lista de `falas` com `quem`.
- Formato do contrato = **híbrido** (md humano → json compilado).
- Ordem de construção = **fundação primeiro** (contrato → story-engine → filme).
- Campos do contrato em **português**. ✔
- **Música + SFX = parte da v1** (não opcional; áudio é barato, itera por re-mux). ✔
- **Prioridade de direção v1 = movimento constante + alta troca de imagem** (sem
  vídeo generativo): planos curtos (`tempo_s` ≈ 2–3 s), câmera sempre ativa, e
  reuso de imagem em vários planos pra subir o turnover sem estourar custo. ✔
- **Menu fixo (enum)** para `funcao_retencao` e `emocao` (§12). ✔

## 8. Motores de IA de vídeo — PARADOS (custo)

Existem instalados e funcionais, mas **não** entram na v1 (decisão de custo):
`skyreelsv3` (SkyReels V3, **A2V talking-avatar** resolve falas com lip-sync,
porta 7860 — **colide com a porta do inemavox TTS**) e `VideosDGX2` (Wan 2.2,
porta 7862). Detalhes em `pixflow/FUTURO-MOTORES-IA-VIDEO.md` e
`inemaref/FUTURO-MOTORES-IA-VIDEO.md`. Como o renderizador é plugável, no futuro
um beat de personagem falando pode ir no SkyReels A2V sem mudar o contrato.

## 9. Erro, idempotência e custo

- **Idempotente** (padrão inemaref): pular imagens/render já existentes; permitir
  retomar.
- **Áudio é barato, imagem/render é caro** (padrão pixflow-trailer): iterar
  narração via **re-mux**, sem re-renderizar.
- **Guarda de custo:** parâmetro `max_planos`; o validador avisa se a história
  estourar o teto.
- **Piloto antes do full:** renderizar 1–2 beats de amostra (e/ou preview das
  cenas) antes de comprometer ~80 imagens — padrão que você já usa em outras
  skills.

## 10. Organização do repo

```
~/projetos/inemafilme/
  DESIGN.md            ← este documento
  contrato/            ← spec do formato historia (md+json) + exemplo + validador
  story-engine/        ← skill 1 (SKILL.md, scripts/, knowledge/)
  filme/               ← skill 2 (SKILL.md, scripts/)
  README.md
```

- `story-engine/` e `filme/` symlinkados em `~/.claude/skills/` → chamáveis de
  qualquer projeto (é o que torna o `story-engine` **compartilhado**).
- `story-engine/` autocontido → pode virar repo próprio depois, sem reescrever.
- **Filmes gerados** vão pra `~/projetos/output/<id>/` (regra global); o repo
  guarda só o código.

## 11. Ordem de construção (specs seguintes)

1. **Contrato `historia`** — fechar md+json + validador + exemplo (pequeno).
2. **`story-engine` v1** — knowledge colhido + compilar + validar (este é o
   primeiro plano de implementação).
3. **`filme` v1** — spec próprio (direção→imagens→render→narração).
4. *(depois)* migração do `inemaref-serie` pra consumir o contrato; v2/v3.

## 12. Decisões da revisão (2026-06-23)

- **Campos em português** ✔ (confirmado).
- **Música + SFX = parte da v1** ✔ (confirmado; áudio é central).
- **`funcao_retencao` e `emocao` = menu fixo (enum)** ✔ (confirmado;
   extensível). Valores:
  - `funcao_retencao`: cold_open · promessa · escalada · virada · clímax ·
    respiro · payoff · gancho_proximo
  - `emocao`: tensão · medo · melancolia · esperança · euforia · mistério ·
    ternura · fúria
- **Motor de retenção (promessa central + loops)** ✔ é peça de primeira classe
  (§3.3), verificado pelo validador.
- **Prioridade de direção = movimento + alta troca de imagem** ✔ (§5.1).
