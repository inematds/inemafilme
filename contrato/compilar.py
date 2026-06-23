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


def compilar(texto):
    header, corpo = parse_frontmatter(texto)
    doc = {"versao_contrato": VERSAO_CONTRATO}
    doc.update(header)
    doc["personagens"] = parse_personagens(corpo)
    doc["beats"] = parse_beats(corpo)
    return doc
