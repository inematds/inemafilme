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
