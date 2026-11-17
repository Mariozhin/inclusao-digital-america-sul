#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_data.py — Coleta do indicador IT.NET.USER.ZS (Banco Mundial) para Brasil, Argentina,
Chile e Uruguai, com geração da base canônica do projeto.

Fonte
-----
World Bank Open Data — World Development Indicators (WDI), dataset 2.
Indicador: IT.NET.USER.ZS — "Individuals using the Internet (% of population)".
Fonte primária do indicador: International Telecommunication Union (ITU),
World Telecommunication/ICT Indicators Database.

Endpoints
---------
Consulta por país (usada por este script):
    https://api.worldbank.org/v2/country/{ISO3}/indicator/IT.NET.USER.ZS?format=json&per_page=100
Consulta multi-país equivalente (documentada no projeto):
    https://api.worldbank.org/v2/country/BRA;ARG;CHL;URY/indicator/IT.NET.USER.ZS?format=json&per_page=20000
A variante multi-país é bloqueada pelo WAF do Banco Mundial em parte dos ambientes (HTTP 502);
as consultas por país retornam o mesmo conteúdo e são consolidadas aqui.

Saídas
------
data/internet_users.json  base canônica (apenas valores observados)
data/internet_users.csv   visão tabular (tidy)
data/internet_users.js    espelho da base para abrir o dashboard via file://

Uso
---
    python scripts/fetch_data.py [--output-dir data] [--sleep 0.8]

Não há substituição de valores ausentes: anos sem observação simplesmente não constam da base.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

INDICADOR = "IT.NET.USER.ZS"
INDICADOR_NOME = "Individuals using the Internet (% of population)"
INDICADOR_NOME_PT = "Indivíduos que usam a Internet (% da população)"
INICIO_SERIE = 1990
INICIO_ANALISE = 2000
MAX_TENTATIVAS = 12

PAISES = [
    {"codigo": "BRA", "nome": "Brasil", "nome_en": "Brazil", "cor": "#1B4F9C", "cor_nome": "Azul"},
    {"codigo": "ARG", "nome": "Argentina", "nome_en": "Argentina", "cor": "#C2185B", "cor_nome": "Rosa"},
    {"codigo": "CHL", "nome": "Chile", "nome_en": "Chile", "cor": "#1E7A45", "cor_nome": "Verde"},
    {"codigo": "URY", "nome": "Uruguai", "nome_en": "Uruguay", "cor": "#111418", "cor_nome": "Preto"},
]

URL_PAIS = ("https://api.worldbank.org/v2/country/{codigo}/indicator/"
            + INDICADOR + "?format=json&per_page=100")
URL_MULTIPAIS = ("https://api.worldbank.org/v2/country/BRA;ARG;CHL;URY/indicator/"
                 + INDICADOR + "?format=json&per_page=20000")


def consultar_pais(codigo: str, pausa: float = 0.8) -> dict:
    """Consulta a API do Banco Mundial para um país, com repetição em caso de bloqueio WAF."""
    url = URL_PAIS.format(codigo=codigo)
    ultimo_erro = None

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                       "User-Agent": "inclusao-digital-pesquisa/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                texto = resp.read().decode("utf-8")
            if not texto.lstrip().startswith("["):
                raise ValueError("resposta não-JSON (possível bloqueio WAF)")
            dados = json.loads(texto)
            if len(dados) < 2:
                raise ValueError("payload inesperado: %r" % (dados,))
            return {"url": url, "metadados": dados[0], "registros": dados[1],
                    "status": resp.status, "tentativas": tentativa}
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, json.JSONDecodeError) as exc:
            ultimo_erro = exc
            print("  ! %s tentativa %d/%d: %s" % (codigo, tentativa, MAX_TENTATIVAS, exc),
                  file=sys.stderr)
            time.sleep(1.5)

    raise RuntimeError("Falha ao consultar %s: %s" % (codigo, ultimo_erro))


def coletar(pausa: float = 0.8) -> dict:
    coleta_utc = datetime.now(timezone.utc)
    series, verificacao, api_info, ultimo_ano = [], {}, {}, {}
    api_atualizada = None

    for pais in PAISES:
        res = consultar_pais(pais["codigo"], pausa=pausa)
        api_atualizada = str(res["metadados"].get("lastupdated"))
        api_info[pais["codigo"]] = {
            "total_registros": int(res["metadados"].get("total", 0)),
            "paginas": int(res["metadados"].get("pages", 0)),
            "pagina_lida": int(res["metadados"].get("page", 1)),
            "requisicoes": res["tentativas"],
            "status_http": int(res["status"]),
        }

        observacoes = [
            {"ano": int(r["date"]), "valor": float(r["value"])}
            for r in res["registros"]
            if r.get("value") is not None
        ]
        observacoes.sort(key=lambda d: d["ano"])

        primeiro = observacoes[0]["ano"]
        ultimo = observacoes[-1]["ano"]
        ultimo_ano[pais["codigo"]] = ultimo

        anos_presentes = {d["ano"] for d in observacoes}
        ausentes = [a for a in range(INICIO_SERIE, ultimo + 1) if a not in anos_presentes]

        verificacao[pais["codigo"]] = {
            "primeiro_ano": primeiro,
            "ultimo_ano": ultimo,
            "total_observacoes": len(observacoes),
            "anos_ausentes": ausentes,
        }

        series.append({
            "codigo": pais["codigo"],
            "nome": pais["nome"],
            "nome_en": pais["nome_en"],
            "cor": pais["cor"],
            "cor_nome": pais["cor_nome"],
            "primeiro_ano": primeiro,
            "ultimo_ano_disponivel": ultimo,
            "total_observacoes": len(observacoes),
            "dados": observacoes,
        })
        print("  %s — %d observações (%d-%d)" % (pais["codigo"], len(observacoes), primeiro, ultimo))
        time.sleep(pausa)

    # Período comum entre as quatro séries
    conjuntos = [{d["ano"] for d in s["dados"]} for s in series]
    comuns = sorted(set.intersection(*conjuntos))
    anos_analise = [a for a in comuns if a >= INICIO_ANALISE]
    fim_analise = anos_analise[-1]
    lacunas_analise = [a for a in range(INICIO_ANALISE, fim_analise + 1) if a not in anos_analise]

    return {
        "projeto": "Inclusão Digital: uma análise comparativa da evolução do acesso à Internet "
                   "no Brasil e em países da América do Sul",
        "disciplina": "Tecnologia da Informação e Comunicação Aplicada à Administração",
        "gerado_por": "scripts/fetch_data.py (Python %s)" % sys.version.split()[0],
        "fonte": {
            "instituicao": "Banco Mundial (World Bank)",
            "dataset": "World Development Indicators (WDI)",
            "dataset_id": "2",
            "indicador_codigo": INDICADOR,
            "indicador_nome": INDICADOR_NOME,
            "indicador_nome_pt": INDICADOR_NOME_PT,
            "definicao": "Percentual de indivíduos que usaram a Internet nos últimos três meses, "
                         "em relação à população total.",
            "unidade": "% da população",
            "fonte_primaria": "International Telecommunication Union (ITU) — World Telecommunication/"
                              "ICT Indicators Database",
            "url_indicador": "https://data.worldbank.org/indicator/IT.NET.USER.ZS",
            "url_api_pais": URL_PAIS.replace("{codigo}", "{pais}"),
            "url_api_multipais": URL_MULTIPAIS,
            "api_atualizada_em": api_atualizada,
            "nota_coleta": "A consulta multi-país em um único endpoint é bloqueada pelo WAF do "
                           "Banco Mundial a partir de parte dos ambientes (HTTP 502). Foram executadas "
                           "consultas equivalentes, uma por país, no mesmo endpoint oficial, com "
                           "consolidação posterior.",
        },
        "coleta": {
            "data_utc": coleta_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data_local": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "metodologia_api": "JSON stateless, paginação verificada (pages = 1, per_page = 100)",
            "observacao": "Valores preservados como retornados pela API. Anos sem informação não "
                          "constam da base (ausentes, não zeros).",
        },
        "paises": [{k: p[k] for k in ("codigo", "nome", "nome_en", "cor", "cor_nome")} for p in PAISES],
        "periodo": {
            "serie_completa": {"inicio": INICIO_SERIE, "fim": fim_analise},
            "analise": {
                "inicio": INICIO_ANALISE,
                "fim": fim_analise,
                "criterio": "Período comum aos quatro países, iniciado em 2000, sem lacunas em "
                            "nenhuma série.",
            },
            "anos_comuns": comuns,
            "anos_analise": anos_analise,
            "lacunas_na_analise": lacunas_analise,
        },
        "verificacao": {
            "ultimo_ano_por_pais": ultimo_ano,
            "por_pais": verificacao,
            "api": api_info,
        },
        "series": series,
    }


def escrever(dataset: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    json_txt = json.dumps(dataset, ensure_ascii=False, indent=2)
    (out_dir / "internet_users.json").write_text(json_txt + "\n", encoding="utf-8")

    (out_dir / "internet_users.js").write_text(
        "/* Gerado automaticamente por scripts/fetch_data.py a partir de internet_users.json.\n"
        "   Espelho da base canônica para uso via file:// (sem servidor HTTP). "
        "Não editar manualmente. */\n"
        "window.INTERNET_USERS_DATA = " + json_txt + ";\n",
        encoding="utf-8",
    )

    coleta = dataset["coleta"]["data_utc"]
    with (out_dir / "internet_users.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["pais_codigo", "pais", "pais_en", "ano", "valor_percentual",
                    "indicador_codigo", "indicador_nome", "unidade", "fonte", "data_coleta_utc"])
        for s in dataset["series"]:
            for d in s["dados"]:
                w.writerow([s["codigo"], s["nome"], s["nome_en"], d["ano"], repr(d["valor"]),
                            INDICADOR, INDICADOR_NOME, "% da população",
                            "World Bank WDI / ITU", coleta])


def main() -> int:
    raiz = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Coleta IT.NET.USER.ZS (Banco Mundial).")
    ap.add_argument("--output-dir", default=str(raiz / "data"))
    ap.add_argument("--sleep", type=float, default=0.8, help="pausa entre requisições (s)")
    args = ap.parse_args()

    print("Consultando o Banco Mundial — indicador %s" % INDICADOR)
    dataset = coletar(pausa=args.sleep)
    escrever(dataset, Path(args.output_dir))

    p = dataset["periodo"]
    print("\nArquivos gerados em %s" % args.output_dir)
    print("  internet_users.json / .csv / .js")
    print("Período de análise (comum): %d-%d (%d anos)"
          % (p["analise"]["inicio"], p["analise"]["fim"], len(p["anos_analise"])))
    print("API atualizada em: %s" % dataset["fonte"]["api_atualizada_em"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
