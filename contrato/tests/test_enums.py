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
