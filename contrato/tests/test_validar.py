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


import enums


def test_retencao_exemplo_aprova():
    rel = validar.validar(doc_ok())
    assert rel["ok"] is True, rel["erros"]


def test_retencao_sem_promessa_reprova():
    d = doc_ok(); d["promessa_central"] = ""
    erros, _ = validar.validar_retencao(d)
    assert any("promessa" in e for e in erros)


def test_retencao_deserto_reprova():
    d = doc_ok(); d["beats"][0]["loop"] = {"abre": [], "fecha": []}
    erros, _ = validar.validar_retencao(d)
    assert any("deserto" in e for e in erros)


def test_retencao_promessa_fechada_cedo_reprova():
    d = doc_ok()
    d["beats"][4]["loop"] = {"abre": ["vinculo-neytiri"], "fecha": ["promessa-central"]}
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


import subprocess

CONTRATO_DIR = os.path.join(AQUI, "..")


def test_cli_aprova_exemplo():
    r = subprocess.run(
        [sys.executable, "validar.py", "exemplo/historia.json"],
        cwd=CONTRATO_DIR, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OK" in r.stdout


def test_exemplo_exercita_retencao():
    d = doc_ok()
    funcs = {b["funcao_retencao"] for b in d["beats"]}
    for obrig in ("cold_open", "promessa", "escalada", "virada", "climax", "payoff"):
        assert obrig in funcs, f"exemplo nao cobre {obrig}"
    emocoes = {b["emocao"] for b in d["beats"]}
    assert len(emocoes) >= 6, "exemplo pouco variado emocionalmente"
    abre = [b["id"] for b in d["beats"] if enums.ID_PROMESSA in (b["loop"] or {}).get("abre", [])]
    fecha = [b for b in d["beats"] if enums.ID_PROMESSA in (b["loop"] or {}).get("fecha", [])]
    assert abre and fecha
    assert fecha[0]["funcao_retencao"] == "payoff"
