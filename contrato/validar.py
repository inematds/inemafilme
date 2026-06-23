#!/usr/bin/env python3
"""Valida historia.json: schema + checklist de retencao. Stdlib apenas."""
import json
import sys

from enums import FUNCOES_RETENCAO, EMOCOES, FORMATOS, ID_PROMESSA

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
