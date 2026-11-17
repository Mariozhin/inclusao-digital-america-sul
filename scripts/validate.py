#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate.py — Auditoria da base de dados e recálculo independente das métricas do projeto.

Verifica:
  1. Estrutura e integridade do JSON (chaves obrigatórias, duplicidades, ordenação, faixa 0-100).
  2. Coerência entre a base canônica, o espelho JS e o CSV.
  3. Existência de lacunas no período de análise (2000-2024).
  4. Recálculo independente das métricas citadas em docs/analise-administrativa.md,
     no dashboard e no relatório (pontos percentuais, médias, diferenças, liderança).
  5. (Opcional) Comparação com uma execução anterior da coleta, via --baseline.

Uso:
    python scripts/validate.py [--baseline CAMINHO/internet_users.json] [--json-saida output/validacao.json]
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

PAISES = ["BRA", "ARG", "CHL", "URY"]
ESTRANGEIROS = ["ARG", "CHL", "URY"]
NOMES = {"BRA": "Brasil", "ARG": "Argentina", "CHL": "Chile", "URY": "Uruguai"}


class Auditor:
    def __init__(self) -> None:
        self.falhas: list[str] = []
        self.avisos: list[str] = []
        self.ok: list[str] = []

    def check(self, condicao: bool, mensagem: str) -> bool:
        if condicao:
            self.ok.append(mensagem)
        else:
            self.falhas.append(mensagem)
        return condicao

    def aviso(self, mensagem: str) -> None:
        self.avisos.append(mensagem)


def carregar(caminho: Path) -> dict:
    with caminho.open(encoding="utf-8") as fh:
        return json.load(fh)


def indexar(dataset: dict) -> dict[str, dict[int, float]]:
    return {s["codigo"]: {d["ano"]: d["valor"] for d in s["dados"]} for s in dataset["series"]}


def valor(idx: dict, codigo: str, ano: int):
    return idx[codigo].get(ano)


def media(vals) -> float | None:
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def metricas(dataset: dict) -> dict:
    idx = indexar(dataset)
    anos = dataset["periodo"]["anos_analise"]
    out: dict = {"periodo": {"inicio": anos[0], "fim": anos[-1], "n": len(anos)}, "paises": {}}

    for c in PAISES:
        vals = [valor(idx, c, a) for a in anos]
        primeiro, ultimo = vals[0], vals[-1]
        variacoes = [(anos[i], vals[i] - vals[i - 1]) for i in range(1, len(anos))]
        maior_alta = max(variacoes, key=lambda t: t[1])
        maior_queda = min(variacoes, key=lambda t: t[1])
        out["paises"][c] = {
            "nome": NOMES[c],
            "primeiro_ano": anos[0],
            "primeiro_valor": round(primeiro, 6),
            "ultimo_ano": anos[-1],
            "ultimo_valor": round(ultimo, 6),
            "delta_pp": round(ultimo - primeiro, 6),
            "variacao_relativa_pct": round((ultimo - primeiro) / primeiro * 100, 4),
            "media_periodo": round(media(vals), 6),
            "minimo": round(min(vals), 6),
            "maximo": round(max(vals), 6),
            "maior_alta_anual": {"ano": maior_alta[0], "delta_pp": round(maior_alta[1], 6)},
            "maior_queda_anual": {"ano": maior_queda[0], "delta_pp": round(maior_queda[1], 6)},
            "anos_de_queda": [a for a, d in variacoes if d < 0],
        }

    media_est = {a: media([valor(idx, c, a) for c in ESTRANGEIROS]) for a in anos}
    out["media_estrangeiros"] = {a: round(v, 6) for a, v in media_est.items()}
    out["diferenca_brasil_media"] = {a: round(valor(idx, "BRA", a) - media_est[a], 6) for a in anos}
    out["diferenca_brasil_pais"] = {
        c: {a: round(valor(idx, "BRA", a) - valor(idx, c, a), 6) for a in anos} for c in ESTRANGEIROS
    }

    lider_por_ano, contagem = {}, {c: 0 for c in PAISES}
    for a in anos:
        melhor = max(PAISES, key=lambda c: valor(idx, c, a))
        lider_por_ano[a] = melhor
        contagem[melhor] += 1
    out["lider_por_ano"] = lider_por_ano
    out["contagem_lideranca"] = contagem

    amplitude = {}
    for a in anos:
        vals = [valor(idx, c, a) for c in PAISES]
        amplitude[a] = round(max(vals) - min(vals), 6)
    out["amplitude"] = amplitude

    subperiodos = {}
    for ini, fim in ((2000, 2009), (2010, 2019), (2020, 2024)):
        bloco = {}
        for c in PAISES:
            a, b = valor(idx, c, ini), valor(idx, c, fim)
            bloco[c] = {
                "inicio": round(a, 6), "fim": round(b, 6),
                "delta_pp": round(b - a, 6),
                "pp_por_ano": round((b - a) / (fim - ini), 6),
            }
        subperiodos["%d-%d" % (ini, fim)] = bloco
    out["subperiodos"] = subperiodos

    ultimo = anos[-1]
    out["comparativo_final"] = {
        "ano": ultimo,
        "brasil": round(valor(idx, "BRA", ultimo), 6),
        "media_estrangeiros": round(media_est[ultimo], 6),
        "diferenca_pp": round(valor(idx, "BRA", ultimo) - media_est[ultimo], 6),
    }
    return out


def verificar_base(dataset: dict, aud: Auditor, raiz: Path) -> None:
    chaves = ["projeto", "fonte", "coleta", "paises", "periodo", "verificacao", "series"]
    aud.check(all(k in dataset for k in chaves), "JSON contém todas as chaves de topo obrigatórias")
    aud.check(dataset["fonte"]["indicador_codigo"] == "IT.NET.USER.ZS", "Indicador correto: IT.NET.USER.ZS")
    aud.check([p["codigo"] for p in dataset["paises"]] == PAISES, "Países corretos: BRA, ARG, CHL, URY")

    idx = indexar(dataset)
    total = 0
    for c in PAISES:
        dados = idx[c]
        total += len(dados)
        aud.check(list(dados) == sorted(dados), "%s: anos em ordem crescente" % c)
        aud.check(len(dados) == len(set(dados)), "%s: sem anos duplicados" % c)
        aud.check(all(0 <= v <= 100 for v in dados.values()), "%s: valores dentro de 0-100" % c)
        aud.check(all(v is not None for v in dados.values()), "%s: sem valores nulos" % c)
    aud.check(total == 135, "Total de observações = 135 (encontrado: %d)" % total)

    anos_analise = dataset["periodo"]["anos_analise"]
    aud.check(len(anos_analise) == 25, "Período de análise com 25 anos (2000-2024)")
    aud.check(not dataset["periodo"]["lacunas_na_analise"], "Nenhuma lacuna no período 2000-2024")
    for c in PAISES:
        faltando = [a for a in anos_analise if a not in idx[c]]
        aud.check(not faltando, "%s: sem lacunas em 2000-2024" % c)

    # último ano disponível coerente entre as séries
    ultimos = {c: max(idx[c]) for c in PAISES}
    aud.check(len(set(ultimos.values())) == 1, "Mesmo último ano disponível nos quatro países (%s)"
              % ultimos["BRA"])

    # espelho JS
    js_path = raiz / "data" / "internet_users.js"
    if js_path.exists():
        txt = js_path.read_text(encoding="utf-8")
        m = re.search(r"window\.INTERNET_USERS_DATA\s*=\s*(\{.*\})\s*;\s*$", txt, re.S)
        if aud.check(m is not None, "Espelho JS localizado e legível"):
            js_data = json.loads(m.group(1))
            aud.check(js_data["series"] == dataset["series"],
                      "Espelho JS idêntico ao JSON canônico (séries)")
    else:
        aud.check(False, "Espelho data/internet_users.js ausente")

    # CSV
    csv_path = raiz / "data" / "internet_users.csv"
    if csv_path.exists():
        with csv_path.open(encoding="utf-8") as fh:
            linhas = list(csv.DictReader(fh))
        aud.check(len(linhas) == total, "CSV com %d linhas de dados (esperado %d)" % (len(linhas), total))
        divergencias = 0
        for ln in linhas:
            v_csv = float(ln["valor_percentual"])
            v_json = idx[ln["pais_codigo"]][int(ln["ano"])]
            if abs(v_csv - v_json) > 1e-12:
                divergencias += 1
        aud.check(divergencias == 0, "CSV e JSON com valores idênticos (%d divergências)" % divergencias)
    else:
        aud.check(False, "data/internet_users.csv ausente")

    # nenhum zero artificial em 2000-2024
    zeros = [(c, a) for c in PAISES for a in anos_analise if idx[c][a] == 0]
    aud.check(not zeros, "Nenhum zero artificial no período de análise")


def comparar_baseline(dataset: dict, baseline: dict, aud: Auditor) -> None:
    idx_a, idx_b = indexar(dataset), indexar(baseline)
    aud.check(set(idx_a) == set(idx_b), "Baseline: mesmos países")
    iguais = all(idx_a[c] == idx_b[c] for c in PAISES)
    aud.check(iguais, "Baseline: valores idênticos entre execuções independentes da coleta")
    if not iguais:
        for c in PAISES:
            difs = {a: (idx_a[c].get(a), idx_b[c].get(a)) for a in set(idx_a[c]) | set(idx_b[c])
                    if idx_a[c].get(a) != idx_b[c].get(a)}
            if difs:
                aud.aviso("%s: %d divergências vs. baseline (%r)" % (c, len(difs), list(difs.items())[:3]))


def conferir_textos(m: dict, raiz: Path, aud: Auditor) -> None:
    """Confere se os valores numéricos publicados nos artefatos coincidem com o recálculo."""
    alvos = {
        "docs/analise-administrativa.md": None,
        "output/relatorio-inclusao-digital.html": None,
        "index.html": None,
    }
    amostras = [
        ("%0.2f" % m["comparativo_final"]["brasil"]).replace(".", ","),
        ("%0.2f" % m["comparativo_final"]["media_estrangeiros"]).replace(".", ","),
        ("%0.2f" % m["paises"]["ARG"]["ultimo_valor"]).replace(".", ","),
        ("%0.2f" % m["paises"]["CHL"]["ultimo_valor"]).replace(".", ","),
        ("%0.2f" % m["paises"]["URY"]["ultimo_valor"]).replace(".", ","),
        ("%0.2f" % m["paises"]["BRA"]["delta_pp"]).replace(".", ","),
    ]
    for rel, _ in alvos.items():
        caminho = raiz / rel
        if not caminho.exists():
            aud.aviso("Artefato ainda não gerado: %s" % rel)
            continue
        texto = caminho.read_text(encoding="utf-8", errors="ignore")
        ausentes = [a for a in amostras if a not in texto]
        if ausentes:
            aud.aviso("%s: valores não encontrados no texto: %s" % (rel, ", ".join(ausentes)))
        else:
            aud.ok.append("%s: valores-chave conferem com o recálculo" % rel)


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    raiz = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="")
    ap.add_argument("--json-saida", default=str(raiz / "output" / "validacao.json"))
    args = ap.parse_args()

    dataset = carregar(raiz / "data" / "internet_users.json")
    aud = Auditor()

    verificar_base(dataset, aud, raiz)
    if args.baseline:
        comparar_baseline(dataset, carregar(Path(args.baseline)), aud)

    m = metricas(dataset)
    conferir_textos(m, raiz, aud)

    print("=" * 78)
    print("AUDITORIA DA BASE — indicador IT.NET.USER.ZS (Banco Mundial)")
    print("=" * 78)
    print("Coleta: %s | API atualizada em: %s"
          % (dataset["coleta"]["data_utc"], dataset["fonte"]["api_atualizada_em"]))
    print("Período de análise: %d-%d (%d anos)\n"
          % (m["periodo"]["inicio"], m["periodo"]["fim"], m["periodo"]["n"]))
    print("%-10s %9s %9s %9s %11s %9s" % ("País", "2000", "2024", "Δ pp", "Δ rel.(%)", "média"))
    for c in PAISES:
        p = m["paises"][c]
        print("%-10s %9.2f %9.2f %9.2f %11.1f %9.2f"
              % (p["nome"], p["primeiro_valor"], p["ultimo_valor"], p["delta_pp"],
                 p["variacao_relativa_pct"], p["media_periodo"]))
    print("\nBrasil vs. média dos três países (2024): %.2f vs. %.2f -> Δ %.2f pp"
          % (m["comparativo_final"]["brasil"], m["comparativo_final"]["media_estrangeiros"],
             m["comparativo_final"]["diferenca_pp"]))
    print("Liderança do período (nº de anos na maior taxa): %r" % m["contagem_lideranca"])
    print("Maiores altas anuais: " + " | ".join(
        "%s %d (+%.2f pp)" % (m["paises"][c]["nome"], m["paises"][c]["maior_alta_anual"]["ano"],
                              m["paises"][c]["maior_alta_anual"]["delta_pp"]) for c in PAISES))
    print("Anos com queda: " + " | ".join(
        "%s: %s" % (m["paises"][c]["nome"], m["paises"][c]["anos_de_queda"] or "nenhum") for c in PAISES))

    print("\n" + "-" * 78)
    for msg in aud.ok:
        print("  [OK]    " + msg)
    for msg in aud.avisos:
        print("  [AVISO] " + msg)
    for msg in aud.falhas:
        print("  [FALHA] " + msg)
    print("-" * 78)
    print("Resultado: %d verificações OK, %d avisos, %d falhas"
          % (len(aud.ok), len(aud.avisos), len(aud.falhas)))

    saida = Path(args.json_saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps({
        "dataset": str(raiz / "data" / "internet_users.json"),
        "coleta_utc": dataset["coleta"]["data_utc"],
        "api_atualizada_em": dataset["fonte"]["api_atualizada_em"],
        "metricas": m,
        "auditoria": {"ok": aud.ok, "avisos": aud.avisos, "falhas": aud.falhas},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Métricas e resultado da auditoria: %s" % saida)

    return 1 if aud.falhas else 0


if __name__ == "__main__":
    sys.exit(main())
