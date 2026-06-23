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
