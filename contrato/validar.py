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
