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
