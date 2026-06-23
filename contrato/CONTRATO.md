# Contrato `historia` (inemafilme.historia/v1)

A "junta" do inemafilme. Duas camadas: `historia.md` (humano) → `historia.json`
(máquina), via `compilar.py`. Validado por `validar.py`. **Agnóstico de render.**

## historia.md — gramática

**Frontmatter** (entre `---`): `id`, `titulo`, `logline`, `promessa_central`,
`duracao_alvo_s` (int, segundos), `formato` (`16:9`|`9:16`), `voz_narrador`,
`look_padrao`.

**Comentários de metadado** (`<!-- tipo: k=v | k=v -->`):
- `personagem`: `nome`, `aparencia` (uma linha por personagem do elenco).
- `beat`: `id`, `ato` (1-3), `ordem` (opcional; default = sequência),
  `retencao` (enum), `emocao` (enum), `tempo_s`.
- `loop`: `abre`, `fecha` — **listas** separadas por vírgula (um beat pode abrir
  e/ou fechar vários loops). Ex.: `<!-- loop: fecha=lealdade,guerra | abre=fuga -->`.
- `cena`: `descricao` (visual), `ambiente`, `personagens` (csv), `look` (dica).

**Prosa do beat:** linhas `> ...` = narração (`quem=narrador`); linhas
`[Nome]: ...` = fala de personagem (`quem=nome`, minúsculo). Na v1 só a narração
é usada pelo render; falas de personagem já são registradas para a v2.

## Menus fixos (enums)

- `funcao_retencao`: cold_open · promessa · escalada · virada · climax ·
  respiro · payoff · gancho_proximo
- `emocao`: tensao · medo · melancolia · esperanca · euforia · misterio ·
  ternura · furia
- `formato`: 16:9 · 9:16

(`look` NÃO é validado por enum — é dica de render, decisão do skill `filme`.)

## Regras de retenção (validadas mecanicamente)

- Existe `promessa_central` e um beat `cold_open`/`promessa` no ato 1 que a planta.
- A promessa central é um loop com id **`promessa-central`**, que só pode
  **fechar** num beat `climax`/`payoff` (não antes).
- **Sem "deserto":** depois de cada beat (menos o último) há ≥1 loop aberto.
- Há `escalada` e há `climax`/`payoff`.
- `Σ tempo_s ≈ duracao_alvo_s` (±15%, aviso). `nº de beats ≤ max_planos` (aviso).

## historia.json — forma

```jsonc
{
  "versao_contrato": "inemafilme.historia/v1",
  "id": "...", "titulo": "...", "logline": "...", "promessa_central": "...",
  "duracao_alvo_s": 60, "formato": "16:9", "voz_narrador": "bella",
  "look_padrao": "cinema-dramatico",
  "personagens": [ { "nome": "jake", "aparencia": "..." } ],
  "beats": [
    {
      "id": "b01", "ato": 1, "ordem": 1,
      "funcao_retencao": "cold_open", "emocao": "tensao", "tempo_s": 6,
      "loop": { "abre": ["mundo-perigoso"], "fecha": [] },
      "cena": { "descricao_visual": "...", "ambiente": "...",
                "personagens_em_cena": [], "look_sugerido": "sci-fi-cyberpunk" },
      "falas": [ { "quem": "narrador", "texto": "..." } ]
    }
  ]
}
```

## Uso

```bash
python3 compilar.py historia.md > historia.json
python3 validar.py historia.json      # exit 0 = aprovado
```
