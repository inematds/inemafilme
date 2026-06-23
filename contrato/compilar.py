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
