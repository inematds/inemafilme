---
name: roteiro
description: Transforma um assunto OU uma historia bruta num ROTEIRO estruturado para retencao (historia.md + historia.json), no contrato inemafilme.historia/v1. Agnostico de render. Use quando o usuario pedir para criar/escrever/estruturar o ROTEIRO ou a HISTORIA de um filme/episodio, transformar um assunto em historia com ganchos e arco (promessa central + loops), ou preparar a historia para o sistema de filme (inemafilme) ou para o inemaref. Gatilhos: 'cria o roteiro do filme', 'roteiro do episodio', 'a historia do filme X', 'estrutura a historia', 'roteiro com ganchos/retencao', 'roteiro pra inemafilme/pixflow'. NAO renderiza video.
---

# roteiro

Produz a `historia` (o contrato que liga tudo). **Não renderiza.** Quem renderiza
é o skill `filme` (pixflow) ou o inemaref.

## Entrada (três modos)
- **A — só assunto:** invente a história completa (logline → promessa central →
  arco de 3 atos → beats), aplicando retenção.
- **B — roteiro pronto:** NÃO invente enredo; segmente em beats e injete a
  estrutura de retenção (promessa, loops, escalada, payoff), cortando gordura.
- **C — referências:** se vier aparência de personagem/ambiente, use-a no elenco;
  senão deixe como descrição (o `filme`/inemaref gera depois).

## Como escrever (você, o agente)
1. Leia `knowledge/retencao.md`, `frameworks.md`, `tres-regras.md`.
2. Defina a `promessa_central` (a pergunta dramática) ANTES dos beats.
3. Escreva a narração como texto corrido fluente; só então fatie em beats.
4. Para cada beat, preencha os comentários de metadado conforme
   `../contrato/CONTRATO.md`: `beat`, `loop` (abre/fecha — listas; a promessa
   central é o loop `promessa-central`), `cena` (descrição visual + emoção).
   Mantenha **sempre ≥1 loop aberto** e feche a promessa central só no `payoff`.
5. Salve em `historia.md`.

## Compilar e validar (sempre)
```bash
python3 ../contrato/compilar.py historia.md > historia.json
python3 ../contrato/validar.py historia.json
```
Se o validador apontar ERRO (deserto, promessa fechada cedo, sem climax...),
**corrija a `historia.md` e recompile** antes de entregar. Avisos (tempo/custo)
são opcionais.

## Saída
`historia.md` + `historia.json` (validado). É o que o `filme` consome.
