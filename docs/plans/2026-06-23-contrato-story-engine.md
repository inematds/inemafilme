# Contrato `historia` + `story-engine` v1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar o contrato `historia` (formato + compilador + validador) e o skill `story-engine` v1, que transforma um assunto/roteiro numa `historia.md`/`historia.json` estruturada para retenção — sem renderizar nada.

**Architecture:** O contrato é a "junta" do sistema. Duas camadas: `historia.md` (humano, editável) compilado para `historia.json` (máquina, consumido por renderizadores). As ferramentas do contrato (`compilar.py`, `validar.py`, `enums.py`) vivem em `contrato/` e são reusáveis por qualquer consumidor (story-engine, filme, inemaref). O `story-engine` é um skill (SKILL.md + knowledge) que **escreve** a `historia.md` (trabalho do agente, padrão inemaref) e **chama** as ferramentas do contrato para compilar/validar.

**Tech Stack:** Python 3 (stdlib apenas para `compilar.py`/`validar.py`/`enums.py` — sem dependências externas); `pytest` apenas para os testes; Markdown para SKILL.md e knowledge.

## Global Constraints

- **Campos do contrato em português** (`titulo`, `funcao_retencao`, `quem`, `promessa_central`...).
- **`versao_contrato` = `"inemafilme.historia/v1"`** (string exata).
- **`funcao_retencao` ∈** `cold_open`, `promessa`, `escalada`, `virada`, `climax`, `respiro`, `payoff`, `gancho_proximo` (ascii, sem acento).
- **`emocao` ∈** `tensao`, `medo`, `melancolia`, `esperanca`, `euforia`, `misterio`, `ternura`, `furia` (ascii, sem acento).
- **`formato` ∈** `16:9`, `9:16`.
- **A promessa central é um loop com id literal `promessa-central`** — o validador depende disso.
- **`compilar.py`, `validar.py`, `enums.py` usam só a stdlib** (sem PyYAML, sem libs). `pytest` só nos testes.
- **Toda fala carrega `quem`** (`narrador` na v1; o compilador já registra falas de personagem para a v2).
- **O contrato é agnóstico de render:** a cena é *descrita* (`descricao_visual`, `emocao`), não *dirigida* (câmera/look são do `filme`). `look_sugerido` é dica opcional, não validada por enum.
- **Frequent commits:** um commit por task (último passo de cada task).

---

## File Structure

```
~/projetos/inemafilme/
  contrato/
    enums.py                 # menus fixos + versao_contrato (fonte única)
    compilar.py              # historia.md -> dict/historia.json (stdlib)
    validar.py               # valida dict: schema + retenção (stdlib)
    CONTRATO.md              # spec formal do formato (md + json) — referência humana
    exemplo/
      historia.md            # exemplo canônico (Avatar-mini), exercita todos os enums
      historia.json          # golden compilado (commitado)
    tests/
      test_enums.py
      test_compilar.py
      test_validar.py
  story-engine/
    SKILL.md                 # como o agente escreve a historia.md + chama o contrato
    knowledge/
      retencao.md            # promessa central + loops + curiosity gap + escalada
      frameworks.md          # Save the Cat / Jornada do Herói recalibrados p/ longo
      tres-regras.md         # colhido do inemaref-serie
  docs/plans/2026-06-23-contrato-story-engine.md   # este plano
  requirements-dev.txt       # pytest
  .gitignore
  README.md
```

Boundaries: `enums.py` é a fonte única dos menus (importado por `compilar`/`validar`). `compilar.py` só parseia (md→dict). `validar.py` só valida (dict→relatório). `story-engine/` é prosa + chama os scripts. Cada arquivo tem uma responsabilidade.

---

### Task 1: Scaffold + `enums.py` (fonte única dos menus)

**Files:**
- Create: `requirements-dev.txt`, `.gitignore`, `README.md`
- Create: `contrato/enums.py`
- Test: `contrato/tests/test_enums.py`

**Interfaces:**
- Produces: `enums.VERSAO_CONTRATO: str`, `enums.FUNCOES_RETENCAO: list[str]`, `enums.EMOCOES: list[str]`, `enums.FORMATOS: list[str]`, `enums.ID_PROMESSA: str` (= `"promessa-central"`).

- [ ] **Step 1: Create repo support files**

`requirements-dev.txt`:
```
pytest>=7
```

`.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
.venv/
```

`README.md`:
```markdown
# inemafilme

Sistema de filme/episódio narrado (estilo inemaref, motor pixflow, sem IA de vídeo).
Ver `DESIGN.md` para a arquitetura e `docs/plans/` para os planos.

Sub-projeto 1 (este): contrato `historia` + `story-engine`.
```

- [ ] **Step 2: Install dev deps**

Run: `cd /home/nmaldaner/projetos/inemafilme && python3 -m pip install -r requirements-dev.txt`
Expected: pytest instalado (ou já satisfeito).

- [ ] **Step 3: Write the failing test**

`contrato/tests/test_enums.py`:
```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import enums

def test_versao_contrato():
    assert enums.VERSAO_CONTRATO == "inemafilme.historia/v1"

def test_funcoes_retencao_completas():
    assert enums.FUNCOES_RETENCAO == [
        "cold_open", "promessa", "escalada", "virada",
        "climax", "respiro", "payoff", "gancho_proximo",
    ]

def test_emocoes_completas():
    assert enums.EMOCOES == [
        "tensao", "medo", "melancolia", "esperanca",
        "euforia", "misterio", "ternura", "furia",
    ]

def test_formatos_e_id_promessa():
    assert enums.FORMATOS == ["16:9", "9:16"]
    assert enums.ID_PROMESSA == "promessa-central"
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_enums.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'enums'`.

- [ ] **Step 5: Write minimal implementation**

`contrato/enums.py`:
```python
"""Menus fixos do contrato historia (fonte única). Stdlib apenas."""

VERSAO_CONTRATO = "inemafilme.historia/v1"

FUNCOES_RETENCAO = [
    "cold_open", "promessa", "escalada", "virada",
    "climax", "respiro", "payoff", "gancho_proximo",
]

EMOCOES = [
    "tensao", "medo", "melancolia", "esperanca",
    "euforia", "misterio", "ternura", "furia",
]

FORMATOS = ["16:9", "9:16"]

# A promessa central é rastreada como um loop com este id literal.
ID_PROMESSA = "promessa-central"
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_enums.py -v`
Expected: PASS (4 passed).

- [ ] **Step 7: Commit**

```bash
cd /home/nmaldaner/projetos/inemafilme
git init -q 2>/dev/null; git add -A
git commit -q -m "feat(contrato): scaffold + enums fixos do contrato historia"
```

---

### Task 2: `compilar.py` — frontmatter + personagens

**Files:**
- Create: `contrato/compilar.py`
- Test: `contrato/tests/test_compilar.py`

**Interfaces:**
- Consumes: `enums.VERSAO_CONTRATO`.
- Produces: `compilar.parse_frontmatter(texto: str) -> tuple[dict, str]`; `compilar.parse_personagens(corpo: str) -> list[dict]`; `compilar.compilar(texto: str) -> dict` (parcial nesta task: header + `personagens` + `versao_contrato`; `beats` vem na Task 3).

- [ ] **Step 1: Write the failing test**

`contrato/tests/test_compilar.py`:
```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import compilar

MD_HEADER = '''---
id: teste-01
titulo: "Filme de Teste"
logline: "uma linha"
promessa_central: "vai dar certo?"
duracao_alvo_s: 120
formato: "16:9"
voz_narrador: bella
look_padrao: cinema-dramatico
---

<!-- personagem: nome=jake | aparencia=ex-fuzileiro de cabelo raspado -->
<!-- personagem: nome=neytiri | aparencia=na'vi alta de pele azul -->
'''

def test_frontmatter_basico():
    header, corpo = compilar.parse_frontmatter(MD_HEADER)
    assert header["id"] == "teste-01"
    assert header["titulo"] == "Filme de Teste"
    assert header["duracao_alvo_s"] == 120          # convertido para int
    assert header["formato"] == "16:9"
    assert "personagem" in corpo                     # corpo preservado

def test_personagens():
    _, corpo = compilar.parse_frontmatter(MD_HEADER)
    pers = compilar.parse_personagens(corpo)
    assert pers == [
        {"nome": "jake", "aparencia": "ex-fuzileiro de cabelo raspado"},
        {"nome": "neytiri", "aparencia": "na'vi alta de pele azul"},
    ]

def test_compilar_parcial_header():
    doc = compilar.compilar(MD_HEADER)
    assert doc["versao_contrato"] == "inemafilme.historia/v1"
    assert doc["id"] == "teste-01"
    assert len(doc["personagens"]) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_compilar.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'compilar'`.

- [ ] **Step 3: Write minimal implementation**

`contrato/compilar.py`:
```python
#!/usr/bin/env python3
"""Compila historia.md (humano) -> dict/historia.json (maquina). Stdlib apenas."""
import json
import re
import sys

from enums import VERSAO_CONTRATO

COMENT = re.compile(r"<!--\s*(\w+):\s*(.*?)\s*-->", re.DOTALL)


def parse_frontmatter(texto):
    """Retorna (header_dict, corpo). Frontmatter = bloco entre as primeiras '---'."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", texto, re.DOTALL)
    if not m:
        return {}, texto
    bloco, corpo = m.group(1), m.group(2)
    header = {}
    for linha in bloco.splitlines():
        if ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        header[chave.strip()] = valor.strip().strip('"').strip("'")
    if "duracao_alvo_s" in header:
        header["duracao_alvo_s"] = int(header["duracao_alvo_s"])
    return header, corpo


def _kv(conteudo):
    """'a=1 | b=2' -> {'a': '1', 'b': '2'} (valor vazio vira None)."""
    d = {}
    for par in conteudo.split("|"):
        if "=" not in par:
            continue
        k, _, v = par.partition("=")
        v = v.strip()
        d[k.strip()] = v if v else None
    return d


def parse_personagens(corpo):
    out = []
    for tipo, conteudo in COMENT.findall(corpo):
        if tipo == "personagem":
            kv = _kv(conteudo)
            out.append({"nome": kv.get("nome"), "aparencia": kv.get("aparencia")})
    return out


def compilar(texto):
    header, corpo = parse_frontmatter(texto)
    doc = {"versao_contrato": VERSAO_CONTRATO}
    doc.update(header)
    doc["personagens"] = parse_personagens(corpo)
    doc["beats"] = []  # preenchido na Task 3
    return doc
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_compilar.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
cd /home/nmaldaner/projetos/inemafilme
git add -A && git commit -q -m "feat(contrato): compilar parseia frontmatter e personagens"
```

---

### Task 3: `compilar.py` — beats (meta, loop, cena, narração, falas)

**Files:**
- Modify: `contrato/compilar.py` (adiciona `parse_beats`, completa `compilar`)
- Test: `contrato/tests/test_compilar.py` (adiciona testes de beats)

**Interfaces:**
- Produces: `compilar.parse_beats(corpo: str) -> list[dict]`. Cada beat: `{id, ato, ordem, funcao_retencao, emocao, tempo_s, loop:{abre,fecha}, cena:{descricao_visual,ambiente,personagens_em_cena,look_sugerido}, falas:[{quem,texto}]}`.

- [ ] **Step 1: Write the failing test (append)**

Anexar a `contrato/tests/test_compilar.py`:
```python
MD_BEATS = MD_HEADER + '''
<!-- beat: id=b01 | ato=1 | retencao=cold_open | emocao=tensao | tempo_s=6 -->
<!-- loop: abre=mundo-perigoso -->
<!-- cena: descricao=nave humana cruzando o vazio | ambiente=orbita | personagens= | look=sci-fi-cyberpunk -->
> Em 2154, a Terra esta morta.

<!-- beat: id=b02 | ato=1 | retencao=promessa | emocao=melancolia | tempo_s=10 -->
<!-- loop: abre=promessa-central -->
<!-- cena: descricao=ex-fuzileiro na chuva | ambiente=cidade decadente | personagens=jake -->
> Jake perdeu as pernas numa guerra.
[Jake]: Eu so queria uma razao pra continuar.
'''

def test_dois_beats():
    beats = compilar.parse_beats(MD_BEATS)
    assert len(beats) == 2

def test_beat_meta_e_loop():
    b = compilar.parse_beats(MD_BEATS)[0]
    assert b["id"] == "b01"
    assert b["ato"] == 1
    assert b["ordem"] == 1
    assert b["funcao_retencao"] == "cold_open"
    assert b["emocao"] == "tensao"
    assert b["tempo_s"] == 6
    assert b["loop"] == {"abre": "mundo-perigoso", "fecha": None}

def test_beat_cena():
    b = compilar.parse_beats(MD_BEATS)[0]
    assert b["cena"]["descricao_visual"] == "nave humana cruzando o vazio"
    assert b["cena"]["ambiente"] == "orbita"
    assert b["cena"]["personagens_em_cena"] == []
    assert b["cena"]["look_sugerido"] == "sci-fi-cyberpunk"

def test_beat_falas_narrador_e_personagem():
    b = compilar.parse_beats(MD_BEATS)[1]
    assert b["cena"]["personagens_em_cena"] == ["jake"]
    assert b["falas"][0] == {"quem": "narrador", "texto": "Jake perdeu as pernas numa guerra."}
    assert b["falas"][1] == {"quem": "jake", "texto": "Eu so queria uma razao pra continuar."}

def test_compilar_completo_tem_beats():
    doc = compilar.compilar(MD_BEATS)
    assert len(doc["beats"]) == 2
    assert doc["beats"][0]["funcao_retencao"] == "cold_open"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_compilar.py -v`
Expected: FAIL com `AttributeError: module 'compilar' has no attribute 'parse_beats'`.

- [ ] **Step 3: Write minimal implementation**

Adicionar a `contrato/compilar.py` (antes de `compilar`) a função `parse_beats`, e trocar a linha `doc["beats"] = []` por `doc["beats"] = parse_beats(corpo)`:
```python
def _num(v):
    if v is None:
        return None
    f = float(v)
    return int(f) if f.is_integer() else f


def parse_beats(corpo):
    partes = re.split(r"(<!--\s*beat:.*?-->)", corpo, flags=re.DOTALL)
    beats = []
    ordem = 0
    i = 1
    while i < len(partes):
        cab = partes[i]
        corpo_beat = partes[i + 1] if i + 1 < len(partes) else ""
        i += 2
        ordem += 1
        kv = _kv(COMENT.match(cab).group(2))
        beat = {
            "id": kv.get("id") or f"b{ordem:02d}",
            "ato": int(kv.get("ato") or 1),
            "ordem": int(kv.get("ordem") or ordem),
            "funcao_retencao": kv.get("retencao"),
            "emocao": kv.get("emocao"),
            "tempo_s": _num(kv.get("tempo_s")),
            "loop": {"abre": None, "fecha": None},
            "cena": {},
            "falas": [],
        }
        for tipo, conteudo in COMENT.findall(corpo_beat):
            if tipo == "loop":
                lk = _kv(conteudo)
                beat["loop"] = {"abre": lk.get("abre"), "fecha": lk.get("fecha")}
            elif tipo == "cena":
                ck = _kv(conteudo)
                pers = ck.get("personagens")
                beat["cena"] = {
                    "descricao_visual": ck.get("descricao"),
                    "ambiente": ck.get("ambiente"),
                    "personagens_em_cena": [p.strip() for p in pers.split(",")] if pers else [],
                    "look_sugerido": ck.get("look"),
                }
        for linha in corpo_beat.splitlines():
            linha = linha.strip()
            if linha.startswith(">"):
                beat["falas"].append({"quem": "narrador", "texto": linha[1:].strip()})
            else:
                mf = re.match(r"^\[([^\]]+)\]:\s*(.*)$", linha)
                if mf:
                    beat["falas"].append({"quem": mf.group(1).strip().lower(), "texto": mf.group(2).strip()})
        beats.append(beat)
    return beats
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_compilar.py -v`
Expected: PASS (8 passed).

- [ ] **Step 5: Commit**

```bash
cd /home/nmaldaner/projetos/inemafilme
git add -A && git commit -q -m "feat(contrato): compilar parseia beats (meta, loop, cena, falas)"
```

---

### Task 4: CLI do `compilar` + exemplo canônico (golden)

**Files:**
- Modify: `contrato/compilar.py` (adiciona `main`/`__main__`)
- Create: `contrato/exemplo/historia.md`
- Create: `contrato/exemplo/historia.json` (gerado e commitado como golden)
- Test: `contrato/tests/test_compilar.py` (teste golden)

**Interfaces:**
- Produces: `compilar.py` executável: `python3 compilar.py historia.md > historia.json`.

- [ ] **Step 1: Write the example `historia.md`**

`contrato/exemplo/historia.md`:
```markdown
---
id: avatar-mini
titulo: "Avatar — A Chama e as Cinzas"
logline: "Um fuzileiro paralitico ganha um corpo alienigena e precisa escolher entre dois mundos."
promessa_central: "Jake vai abandonar os humanos pelos Na'vi — e a que preco?"
duracao_alvo_s: 60
formato: "16:9"
voz_narrador: bella
look_padrao: cinema-dramatico
---

<!-- personagem: nome=jake | aparencia=ex-fuzileiro, ~30 anos, cabelo raspado, cicatriz na sobrancelha -->
<!-- personagem: nome=neytiri | aparencia=na'vi alta, pele azul luminescente, olhos ambar -->
<!-- personagem: nome=quaritch | aparencia=coronel humano, mandibula quadrada, cicatrizes -->

<!-- beat: id=b01 | ato=1 | retencao=cold_open | emocao=tensao | tempo_s=6 -->
<!-- loop: abre=mundo-perigoso -->
<!-- cena: descricao=nave humana cruzando o vazio rumo a um gigante gasoso azul | ambiente=orbita de Pandora | personagens= | look=sci-fi-cyberpunk -->
> Em 2154, a Terra esta morta. O que sobrou da humanidade busca um tesouro a anos-luz de casa.

<!-- beat: id=b02 | ato=1 | retencao=promessa | emocao=melancolia | tempo_s=8 -->
<!-- loop: abre=promessa-central -->
<!-- cena: descricao=ex-fuzileiro em cadeira de rodas olhando a chuva pela janela | ambiente=cidade decadente | personagens=jake -->
> Jake Sully perdeu as pernas numa guerra que ja esqueceu o nome. Mas ainda sabe lutar.

<!-- beat: id=b03 | ato=1 | retencao=escalada | emocao=misterio | tempo_s=8 -->
<!-- loop: abre=ameaca-quaritch -->
<!-- cena: descricao=coronel apontando para um mapa da floresta hostil | ambiente=base militar | personagens=quaritch -->
> Mandaram-no a um mundo onde o ar mata em quatro minutos. E onde algo o observava.

<!-- beat: id=b04 | ato=2 | retencao=virada | emocao=medo | tempo_s=8 -->
<!-- loop: fecha=mundo-perigoso | abre=lealdade-em-jogo -->
<!-- cena: descricao=criatura gigante avancando na selva neon enquanto ele corre | ambiente=floresta de Pandora | personagens=jake -->
> Na primeira noite, a floresta tentou devora-lo. Mas uma cacadora o salvou.

<!-- beat: id=b05 | ato=2 | retencao=respiro | emocao=ternura | tempo_s=8 -->
<!-- loop: fecha=ameaca-quaritch | abre=vinculo-neytiri -->
<!-- cena: descricao=duas figuras tocando as testas sob arvores bioluminescentes | ambiente=clareira sagrada | personagens=jake,neytiri -->
> Neytiri lhe ensinou a ver. E, pela primeira vez, Jake pertencia a algum lugar.

<!-- beat: id=b06 | ato=2 | retencao=escalada | emocao=furia | tempo_s=6 -->
<!-- loop: abre=guerra-iminente -->
<!-- cena: descricao=maquinas humanas derrubando arvores ancestrais em chamas | ambiente=floresta devastada | personagens=quaritch -->
> Mas os humanos vieram pelo tesouro. E o tesouro estava embaixo do lar dela.

<!-- beat: id=b07 | ato=3 | retencao=climax | emocao=euforia | tempo_s=8 -->
<!-- loop: fecha=lealdade-em-jogo | fecha=guerra-iminente -->
<!-- cena: descricao=exercito alienigena montado em feras voadoras contra naves | ambiente=ceu de Pandora | personagens=jake,neytiri,quaritch -->
> Jake escolheu seu lado. Liderou os Na'vi contra o ferro e o fogo dos seus.

<!-- beat: id=b08 | ato=3 | retencao=payoff | emocao=esperanca | tempo_s=8 -->
<!-- loop: fecha=promessa-central | fecha=vinculo-neytiri -->
<!-- cena: descricao=corpo humano sendo deixado para tras enquanto os olhos alienigenas se abrem | ambiente=arvore das almas | personagens=jake,neytiri -->
> No fim, ele deixou de ser humano. E nasceu, de olhos abertos, no mundo que escolheu.
```

- [ ] **Step 2: Write the failing golden test (append)**

Anexar a `contrato/tests/test_compilar.py`:
```python
import json

AQUI = os.path.dirname(__file__)
EXEMPLO = os.path.join(AQUI, "..", "exemplo")

def test_golden_exemplo():
    with open(os.path.join(EXEMPLO, "historia.md"), encoding="utf-8") as f:
        doc = compilar.compilar(f.read())
    with open(os.path.join(EXEMPLO, "historia.json"), encoding="utf-8") as f:
        golden = json.load(f)
    assert doc == golden
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_compilar.py::test_golden_exemplo -v`
Expected: FAIL com `FileNotFoundError: .../exemplo/historia.json`.

- [ ] **Step 4: Add the CLI and generate the golden**

Adicionar ao fim de `contrato/compilar.py`:
```python
def main(argv):
    if len(argv) < 2:
        print("uso: compilar.py historia.md", file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        doc = compilar(f.read())
    json.dump(doc, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

Gerar o golden:
Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 compilar.py exemplo/historia.md > exemplo/historia.json`
Expected: cria `exemplo/historia.json` com 8 beats e 3 personagens.

Conferência rápida:
Run: `python3 -c "import json;d=json.load(open('/home/nmaldaner/projetos/inemafilme/contrato/exemplo/historia.json'));print(len(d['beats']),len(d['personagens']),d['versao_contrato'])"`
Expected: `8 3 inemafilme.historia/v1`

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_compilar.py -v`
Expected: PASS (9 passed).

- [ ] **Step 6: Commit**

```bash
cd /home/nmaldaner/projetos/inemafilme
git add -A && git commit -q -m "feat(contrato): CLI do compilar + exemplo canonico (golden)"
```

---

### Task 5: `validar.py` — schema

**Files:**
- Create: `contrato/validar.py`
- Test: `contrato/tests/test_validar.py`

**Interfaces:**
- Consumes: `enums.FUNCOES_RETENCAO`, `enums.EMOCOES`, `enums.FORMATOS`.
- Produces: `validar.validar_schema(doc: dict) -> list[str]` (lista de erros; vazia = ok).

- [ ] **Step 1: Write the failing test**

`contrato/tests/test_validar.py`:
```python
import os, sys, json, copy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import validar

AQUI = os.path.dirname(__file__)
EXEMPLO = os.path.join(AQUI, "..", "exemplo", "historia.json")

def doc_ok():
    with open(EXEMPLO, encoding="utf-8") as f:
        return json.load(f)

def test_schema_exemplo_sem_erros():
    assert validar.validar_schema(doc_ok()) == []

def test_schema_header_faltando():
    d = doc_ok(); d.pop("promessa_central")
    erros = validar.validar_schema(d)
    assert any("promessa_central" in e for e in erros)

def test_schema_formato_invalido():
    d = doc_ok(); d["formato"] = "4:3"
    assert any("formato" in e for e in validar.validar_schema(d))

def test_schema_funcao_e_emocao_invalidas():
    d = doc_ok()
    d["beats"][0]["funcao_retencao"] = "inventada"
    d["beats"][1]["emocao"] = "raiva"
    erros = validar.validar_schema(d)
    assert any("funcao_retencao" in e for e in erros)
    assert any("emocao" in e for e in erros)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_validar.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'validar'`.

- [ ] **Step 3: Write minimal implementation**

`contrato/validar.py`:
```python
#!/usr/bin/env python3
"""Valida historia.json: schema + checklist de retencao. Stdlib apenas."""
import json
import sys

from enums import FUNCOES_RETENCAO, EMOCOES, FORMATOS

CAMPOS_HEADER = [
    "versao_contrato", "id", "titulo", "promessa_central",
    "duracao_alvo_s", "formato", "voz_narrador", "beats",
]


def validar_schema(doc):
    erros = []
    for c in CAMPOS_HEADER:
        if not doc.get(c):
            erros.append(f"header: campo obrigatorio ausente/vazio: {c}")
    if doc.get("formato") and doc["formato"] not in FORMATOS:
        erros.append(f"header: formato invalido: {doc['formato']} (use {FORMATOS})")
    for b in (doc.get("beats") or []):
        bid = b.get("id", "?")
        if b.get("funcao_retencao") not in FUNCOES_RETENCAO:
            erros.append(f"beat {bid}: funcao_retencao invalida: {b.get('funcao_retencao')}")
        if b.get("emocao") not in EMOCOES:
            erros.append(f"beat {bid}: emocao invalida: {b.get('emocao')}")
        if not isinstance(b.get("tempo_s"), (int, float)) or (b.get("tempo_s") or 0) <= 0:
            erros.append(f"beat {bid}: tempo_s deve ser numero > 0")
        if not isinstance(b.get("falas"), list):
            erros.append(f"beat {bid}: falas deve ser lista")
        if not (b.get("cena") or {}).get("descricao_visual"):
            erros.append(f"beat {bid}: cena.descricao_visual ausente")
    return erros
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_validar.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
cd /home/nmaldaner/projetos/inemafilme
git add -A && git commit -q -m "feat(contrato): validar_schema do contrato historia"
```

---

### Task 6: `validar.py` — checklist de retenção

**Files:**
- Modify: `contrato/validar.py` (adiciona `validar_retencao` e `validar`)
- Test: `contrato/tests/test_validar.py` (testes de retenção)

**Interfaces:**
- Consumes: `enums.ID_PROMESSA`.
- Produces: `validar.validar_retencao(doc, max_planos=160, tolerancia=0.15) -> tuple[list[str], list[str]]` (erros, avisos); `validar.validar(doc, **kw) -> dict` (`{ok, erros, avisos}`).

- [ ] **Step 1: Write the failing test (append)**

Anexar a `contrato/tests/test_validar.py`:
```python
import enums

def test_retencao_exemplo_aprova():
    rel = validar.validar(doc_ok())
    assert rel["ok"] is True, rel["erros"]

def test_retencao_sem_promessa_reprova():
    d = doc_ok(); d["promessa_central"] = ""
    # schema pega o vazio; retenção também exige a promessa
    erros, _ = validar.validar_retencao(d)
    assert any("promessa" in e for e in erros)

def test_retencao_deserto_reprova():
    # remove a abertura de loop do beat 1 -> apos b01 nada aberto
    d = doc_ok(); d["beats"][0]["loop"] = {"abre": None, "fecha": None}
    erros, _ = validar.validar_retencao(d)
    assert any("deserto" in e for e in erros)

def test_retencao_promessa_fechada_cedo_reprova():
    # fecha a promessa-central num beat de respiro (b05), nao no payoff
    d = doc_ok()
    d["beats"][4]["loop"] = {"abre": "vinculo-neytiri", "fecha": "promessa-central"}
    erros, _ = validar.validar_retencao(d)
    assert any("promessa-central fechada cedo" in e for e in erros)

def test_retencao_sem_climax_reprova():
    d = doc_ok()
    for b in d["beats"]:
        if b["funcao_retencao"] in ("climax", "payoff"):
            b["funcao_retencao"] = "respiro"
    erros, _ = validar.validar_retencao(d)
    assert any("climax/payoff" in e for e in erros)

def test_validar_integra_schema_e_retencao():
    d = doc_ok(); d["beats"][0]["emocao"] = "raiva"  # erro de schema
    rel = validar.validar(d)
    assert rel["ok"] is False
    assert any("emocao" in e for e in rel["erros"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_validar.py -v`
Expected: FAIL com `AttributeError: module 'validar' has no attribute 'validar_retencao'`.

- [ ] **Step 3: Write minimal implementation**

Adicionar a `contrato/validar.py` (após `validar_schema`), incluindo o import de `ID_PROMESSA`:
```python
from enums import ID_PROMESSA  # adicionar ao topo, junto dos outros imports de enums

PAYOFF = ("climax", "payoff")


def validar_retencao(doc, max_planos=160, tolerancia=0.15):
    erros, avisos = [], []
    beats = sorted(doc.get("beats") or [], key=lambda b: b.get("ordem", 0))

    if not doc.get("promessa_central"):
        erros.append("retencao: promessa_central ausente")
    planta = [b for b in beats
              if b.get("ato") == 1 and b.get("funcao_retencao") in ("cold_open", "promessa")]
    if not planta:
        erros.append("retencao: nenhum beat de cold_open/promessa no ato 1 planta a promessa")

    abertos = {}
    for idx, b in enumerate(beats):
        loop = b.get("loop") or {}
        fecha, abre = loop.get("fecha"), loop.get("abre")
        if fecha:
            if fecha not in abertos:
                avisos.append(f"beat {b.get('id')}: fecha loop '{fecha}' que nunca abriu")
            else:
                del abertos[fecha]
            if fecha == ID_PROMESSA and b.get("funcao_retencao") not in PAYOFF:
                erros.append(f"beat {b.get('id')}: promessa-central fechada cedo (fora de climax/payoff)")
        if abre:
            abertos[abre] = idx
        ultimo = idx == len(beats) - 1
        if not ultimo and not abertos:
            erros.append(f"beat {b.get('id')}: 'deserto' — nenhum loop aberto apos este beat")
    if abertos:
        restantes = ", ".join(abertos)
        if beats and beats[-1].get("funcao_retencao") == "gancho_proximo":
            avisos.append(f"retencao: loops abertos no fim (cliffhanger ok): {restantes}")
        else:
            avisos.append(f"retencao: loops nunca fechados: {restantes}")

    funcs = {b.get("funcao_retencao") for b in beats}
    if "escalada" not in funcs:
        avisos.append("retencao: nenhuma 'escalada' — a tensao pode nao subir")
    if not (funcs & set(PAYOFF)):
        erros.append("retencao: sem climax/payoff — a promessa nunca eh paga")

    soma = sum(b.get("tempo_s", 0) for b in beats)
    alvo = doc.get("duracao_alvo_s") or 0
    if alvo and abs(soma - alvo) > tolerancia * alvo:
        avisos.append(f"tempo: soma dos beats {soma:.0f}s vs alvo {alvo}s (fora de +-{int(tolerancia*100)}%)")

    if len(beats) > max_planos:
        avisos.append(f"custo: {len(beats)} beats > max_planos {max_planos}")

    return erros, avisos


def validar(doc, **kw):
    erros = validar_schema(doc)
    if erros:
        return {"ok": False, "erros": erros, "avisos": []}
    erros_r, avisos = validar_retencao(doc, **kw)
    return {"ok": not erros_r, "erros": erros_r, "avisos": avisos}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_validar.py -v`
Expected: PASS (10 passed).

- [ ] **Step 5: Commit**

```bash
cd /home/nmaldaner/projetos/inemafilme
git add -A && git commit -q -m "feat(contrato): checklist de retencao (promessa, loops, deserto, escalada)"
```

---

### Task 7: CLI do `validar` + o golden aprova ponta a ponta

**Files:**
- Modify: `contrato/validar.py` (adiciona `main`/`__main__`)
- Test: `contrato/tests/test_validar.py` (teste do CLI por exit code)

**Interfaces:**
- Produces: `validar.py` executável: `python3 validar.py historia.json` → relatório + exit code (0 aprova, 1 reprova).

- [ ] **Step 1: Write the failing test (append)**

Anexar a `contrato/tests/test_validar.py`:
```python
import subprocess

CONTRATO_DIR = os.path.join(AQUI, "..")

def test_cli_aprova_exemplo():
    r = subprocess.run(
        [sys.executable, "validar.py", "exemplo/historia.json"],
        cwd=CONTRATO_DIR, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OK" in r.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_validar.py::test_cli_aprova_exemplo -v`
Expected: FAIL (retorno 2 / "uso:" — sem `main` ainda; ou exit não-0).

- [ ] **Step 3: Add the CLI**

Adicionar ao fim de `contrato/validar.py`:
```python
def main(argv):
    if len(argv) < 2:
        print("uso: validar.py historia.json", file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        doc = json.load(f)
    rel = validar(doc)
    for e in rel["erros"]:
        print("ERRO:", e)
    for a in rel["avisos"]:
        print("aviso:", a)
    print("OK" if rel["ok"] else "REPROVADO")
    return 0 if rel["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run test to verify it passes (full suite)**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/ -v`
Expected: PASS (todos: enums 4 + compilar 9 + validar 11).

Conferência manual do CLI:
Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 validar.py exemplo/historia.json; echo "exit=$?"`
Expected: imprime `OK` e `exit=0`.

- [ ] **Step 5: Commit**

```bash
cd /home/nmaldaner/projetos/inemafilme
git add -A && git commit -q -m "feat(contrato): CLI do validar (exit code) + suite verde"
```

---

### Task 8: skill `story-engine` (SKILL.md + knowledge) + `CONTRATO.md` + integração

**Files:**
- Create: `contrato/CONTRATO.md`
- Create: `story-engine/SKILL.md`
- Create: `story-engine/knowledge/retencao.md`
- Create: `story-engine/knowledge/frameworks.md`
- Create: `story-engine/knowledge/tres-regras.md`
- Test: `contrato/tests/test_validar.py` (teste de cobertura do exemplo)

**Interfaces:**
- Consumes: `compilar.py`, `validar.py` (o skill os invoca).
- Produces: skill `story-engine` instalável; documento `CONTRATO.md` (referência humana do formato).

- [ ] **Step 1: Write the coverage test (append) — failing**

Anexar a `contrato/tests/test_validar.py` (garante que o exemplo canônico exercita a gramática de retenção que o skill ensina):
```python
def test_exemplo_exercita_retencao():
    d = doc_ok()
    funcs = {b["funcao_retencao"] for b in d["beats"]}
    # cobre os pilares que o SKILL.md exige: abre, sustenta e paga a promessa
    for obrig in ("cold_open", "promessa", "escalada", "virada", "climax", "payoff"):
        assert obrig in funcs, f"exemplo nao cobre {obrig}"
    emocoes = {b["emocao"] for b in d["beats"]}
    assert len(emocoes) >= 6, "exemplo pouco variado emocionalmente"
    # a promessa-central abre no ato 1 e fecha no payoff
    abre = [b["id"] for b in d["beats"] if (b["loop"] or {}).get("abre") == enums.ID_PROMESSA]
    fecha = [b for b in d["beats"] if (b["loop"] or {}).get("fecha") == enums.ID_PROMESSA]
    assert abre and fecha
    assert fecha[0]["funcao_retencao"] == "payoff"
```

- [ ] **Step 2: Run test to verify it fails or passes**

Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/test_validar.py::test_exemplo_exercita_retencao -v`
Expected: PASS (o exemplo da Task 4 já cobre). Se FALHAR, corrigir `exemplo/historia.md` e regenerar o golden (Task 4, Step 4) antes de seguir — o exemplo é a referência viva do que o skill ensina.

- [ ] **Step 3: Write `contrato/CONTRATO.md`**

`contrato/CONTRATO.md`:
```markdown
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
- `loop`: `abre`, `fecha` (ids de pergunta; um ou ambos, opcionais).
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

## Regras de retenção (validadas)

- Existe `promessa_central` e um beat `cold_open`/`promessa` no ato 1 que a planta.
- A promessa central é um loop com id **`promessa-central`**, que só pode
  **fechar** num beat `climax`/`payoff` (não antes).
- **Sem "deserto":** depois de cada beat (menos o último) há ≥1 loop aberto.
- Há `escalada` e há `climax`/`payoff`.
- `Σ tempo_s ≈ duracao_alvo_s` (±15%, aviso). `nº de beats ≤ max_planos` (aviso).

## Uso

```bash
python3 compilar.py historia.md > historia.json
python3 validar.py historia.json      # exit 0 = aprovado
```
```

- [ ] **Step 4: Write `story-engine/knowledge/retencao.md`**

`story-engine/knowledge/retencao.md`:
```markdown
# Motor de retenção: a promessa e os loops

O que prende não é o que está acontecendo, é **o que ainda não aconteceu**. A
pessoa fica porque foi *prometido* que algo vem.

## A promessa central
Uma única **pergunta dramática** plantada nos primeiros segundos (cold_open /
promessa) e respondida **só no payoff**. O filme inteiro é a resposta adiada.
Rastreada como um loop de id `promessa-central`.

## Loops aninhados
Cada beat **abre** uma pergunta e/ou **fecha** uma anterior. Regra de ferro:
**nunca deixar um trecho sem nenhum loop aberto** — sempre há algo no ar. Fecha-se
um loop pequeno, mas a promessa central segue aberta até o fim.

## Técnicas
- **Setup → payoff:** planta cedo (objeto, frase, arma), paga tarde.
- **Escalada:** a cada ato o custo sobe; a pergunta fica mais cara de responder.
- **Curiosity gap:** o espectador sabe algo que o personagem não sabe (ou vice).
- **Cliffhanger (gancho_proximo):** em recorrência (v3), fecha o loop pequeno do
  episódio mas abre um maior antes dos créditos. Em filme único, segura a
  promessa central até o payoff.

## Checklist (o validador reprova se faltar)
1. Tem `promessa_central` plantada no ato 1?
2. A promessa só fecha no climax/payoff?
3. Nenhum "deserto" (todo trecho com loop aberto)?
4. Tem escalada e tem climax/payoff?
```

- [ ] **Step 5: Write `story-engine/knowledge/frameworks.md` and `tres-regras.md`**

`story-engine/knowledge/frameworks.md`:
```markdown
# Frameworks de arco (recalibrados para história longa narrada)

Colhido do `video-plan-editor` (estes vêm calibrados p/ vídeo curto viral; aqui
ficam esticados p/ um filme de ~5 min).

## Três atos (espinha)
- **Ato 1 (~25%)** — mundo + protagonista + a promessa (pergunta dramática).
  Beats: cold_open, promessa, primeira escalada.
- **Ato 2 (~50%)** — provações que sobem o custo; uma virada no meio; um respiro
  antes do pior. Beats: escalada, virada, respiro, escalada.
- **Ato 3 (~25%)** — climax (a promessa é confrontada) + payoff (resposta).

## Save the Cat (mapeado p/ funcao_retencao)
abertura→cold_open · tema/promessa→promessa · catalisador/virada→virada ·
diversão&jogos/provações→escalada · pausa→respiro · clímax→climax ·
imagem final→payoff.

## Jornada do Herói (resumo utilizável)
chamado → recusa → mentor/aliado → provações → provação suprema (climax) →
retorno transformado (payoff). Use quando a história é de transformação pessoal.

## Ritmo
Beats curtos no ato 1 (fisgar), respiro no meio do ato 2, aceleração no ato 3.
```

`story-engine/knowledge/tres-regras.md`:
```markdown
# Três regras de conteúdo (colhido do inemaref-serie)

1. **Objetivo + contribuição.** A história tem um objetivo declarado; cada beat
   tem uma contribuição clara (1 frase: o que ele entrega rumo ao objetivo).
   Sem beat decorativo.
2. **Canon visual.** Aparência de personagem/ambiente definida UMA vez (elenco
   em `personagens`) e reusada — consistência entre as cenas.
3. **Narração fluente.** Escrever a locução como **texto corrido** (gancho →
   desenvolvimento → virada → fecho, com conectivos), e SÓ DEPOIS fatiar nos
   beats. Nunca "uma frase solta por cena".
```

- [ ] **Step 6: Write `story-engine/SKILL.md`**

`story-engine/SKILL.md`:
```markdown
---
name: story-engine
description: Transforma um assunto OU um roteiro numa historia estruturada para retencao (historia.md + historia.json), no contrato inemafilme.historia/v1. Agnostico de render. Use quando o usuario pedir para criar/estruturar a historia de um filme/episodio, transformar um assunto em roteiro com ganchos e arco, ou preparar a historia para o sistema de filme (inemafilme) ou para o inemaref. NAO renderiza video.
---

# story-engine

Produz a `historia` (o contrato que liga tudo). **Não renderiza.** Quem rende é o
skill `filme` (pixflow) ou o inemaref.

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
   `../contrato/CONTRATO.md`: `beat`, `loop` (abre/fecha — a promessa central é o
   loop `promessa-central`), `cena` (descrição visual + emoção). Mantenha **sempre
   ≥1 loop aberto** e feche a promessa central só no `payoff`.
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
```

- [ ] **Step 7: Install the skill + run the full suite**

Symlink (torna o skill chamável de qualquer projeto):
Run: `ln -sfn /home/nmaldaner/projetos/inemafilme/story-engine /home/nmaldaner/.claude/skills/story-engine && ls -l /home/nmaldaner/.claude/skills/story-engine`
Expected: symlink criado apontando para o diretório do skill.

Suite completa:
Run: `cd /home/nmaldaner/projetos/inemafilme/contrato && python3 -m pytest tests/ -v`
Expected: PASS (todos verdes, incluindo `test_exemplo_exercita_retencao`).

- [ ] **Step 8: Commit**

```bash
cd /home/nmaldaner/projetos/inemafilme
git add -A && git commit -q -m "feat(story-engine): SKILL.md + knowledge + CONTRATO.md; skill instalado"
```

---

## Self-Review

**1. Spec coverage (DESIGN.md → tasks):**
- Contrato híbrido md+json (§3) → Tasks 2-4 (compilar) + CONTRATO.md (Task 8). ✔
- Campos `promessa_central`, `funcao_retencao`, `emocao`, `tempo_s`, `quem`, `loop`, `personagens` (§3.2) → Tasks 2-3 (parse) + Task 5 (schema). ✔
- Motor de retenção: promessa + loops + deserto + promessa-só-no-payoff (§3.3) → Task 6. ✔
- Enums fixos (§12) → Task 1 + validação Task 5. ✔
- Cena descrita (render-agnóstica), `look_sugerido` não validada por enum (§3, constraints) → Task 3 + Task 5 (sem enum de look). ✔
- story-engine: modos A/B/C, "inteligência = agente", knowledge colhido (§4) → Task 8. ✔
- Guarda de custo `max_planos`, tempo vs duração (§9) → Task 6 (avisos). ✔
- **Fora de escopo deste plano (corretamente):** `filme`/pixflow (§5), consistência via inemaref-folder (§6), motores de IA (§8), migração inemaref. Ganham planos próprios.

**2. Placeholder scan:** Nenhum "TODO/TBD/fill in". Todo passo de código mostra o código; todo comando mostra o esperado. ✔

**3. Type consistency:** `compilar.compilar` retorna o dict consumido por `validar.validar`; `enums.*` (incl. `ID_PROMESSA`) usado consistentemente em compilar/validar/testes; `validar()` retorna `{ok, erros, avisos}` usado igual no CLI (Task 7) e nos testes (Task 6). Nomes de função estáveis entre tasks. ✔

> **Nota de execução:** as Tasks 1-7 são puro TDD verde/vermelho. A Task 8 é
> majoritariamente prosa (skill/knowledge) — seu "teste" é a suíte continuar
> verde + o exemplo canônico exercitar a gramática que o SKILL.md ensina.
