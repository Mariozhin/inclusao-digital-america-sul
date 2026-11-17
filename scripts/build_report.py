#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_report.py — monta o relatório acadêmico (HTML autocontido) e gera o PDF em A4.

Etapas
------
1. Lê o template (report/relatorio.template.html), a folha de estilo (report/relatorio.css),
   a base de dados (data/internet_users.json) e os módulos JavaScript (analytics, svg-chart,
   relatorio) e monta um único arquivo HTML autocontido — sem dependências externas, sem CDN
   e sem servidor.
2. Abre o HTML no Chrome (via Playwright, canal "chrome", sem download de navegador),
   aguarda o carregamento e a renderização dos gráficos SVG e executa a auditoria de
   paginação (detecção de conteúdo que ultrapassa a área útil de cada página).
3. Gera o PDF com página A4, margens zero (controladas pelo CSS) e impressão de fundos.
4. Verifica o PDF resultante: número de páginas, dimensões, presença de texto em cada página
   e ausência de imagens raster (os gráficos são vetoriais).

Uso:
    python scripts/build_report.py [--sem-pdf] [--html-saida CAMINHO] [--pdf-saida CAMINHO]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
OUTPUT = RAIZ / "output"
HTML_SAIDA = OUTPUT / "relatorio-inclusao-digital.html"
PDF_SAIDA = OUTPUT / "relatorio-inclusao-digital.pdf"


def ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def montar_html() -> Path:
    template = ler(RAIZ / "report" / "relatorio.template.html")
    css = ler(RAIZ / "report" / "relatorio.css")
    analytics = ler(RAIZ / "assets" / "js" / "analytics.js")
    svgchart = ler(RAIZ / "assets" / "js" / "svg-chart.js")
    relatorio = ler(RAIZ / "assets" / "js" / "relatorio.js")

    dados = json.loads(ler(RAIZ / "data" / "internet_users.json"))
    dados_compactos = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))

    html = (template
            .replace("{{CSS}}", css)
            .replace("{{DADOS_JS}}", dados_compactos)
            .replace("{{ANALYTICS_JS}}", analytics)
            .replace("{{SVGCHART_JS}}", svgchart)
            .replace("{{RELATORIO_JS}}", relatorio))

    for marcador in ("{{CSS}}", "{{DADOS_JS}}", "{{ANALYTICS_JS}}", "{{SVGCHART_JS}}", "{{RELATORIO_JS}}"):
        if marcador in html:
            raise SystemExit("Marcador não substituído: %s" % marcador)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    HTML_SAIDA.write_text(html, encoding="utf-8")
    print("HTML gerado: %s (%.0f KB)" % (HTML_SAIDA, len(html.encode("utf-8")) / 1024))
    return HTML_SAIDA


def gerar_pdf(html_path: Path, pdf_path: Path) -> list[dict]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        try:
            navegador = pw.chromium.launch(channel="chrome", headless=True)
        except Exception as exc:  # noqa: BLE001
            raise SystemExit(
                "Não foi possível iniciar o Chrome via Playwright (channel='chrome'): %s\n"
                "Alternativa: abra o HTML e use Ctrl+P > Salvar como PDF (A4, margens nenhuma)." % exc
            )

        pagina = navegador.new_page(viewport={"width": 1240, "height": 1000},
                                   device_scale_factor=2)
        pagina.goto(html_path.as_uri(), wait_until="load")
        pagina.wait_for_function("window.__RELATORIO_PRONTO__ === true", timeout=45000)
        pagina.wait_for_timeout(500)

        diagnostico = pagina.evaluate("window.diagnosticarPaginas()")
        paginas_dom = pagina.evaluate("document.querySelectorAll('.page').length")

        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pagina.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        navegador.close()

    print("PDF gerado: %s (%.0f KB)" % (pdf_path, pdf_path.stat().st_size / 1024))
    print("Páginas no HTML: %d" % paginas_dom)

    estouro = [d for d in diagnostico if d["overflowMm"] > 0.5]
    if estouro:
        print("  [ATENÇÃO] páginas com conteúdo excedendo a área útil:")
        for d in estouro:
            print("    página %s: +%.1f mm" % (d["pagina"], d["overflowMm"]))
    else:
        print("  [OK] nenhuma página com estouro de conteúdo")
    return diagnostico


def verificar_pdf(pdf_path: Path, esperado: int) -> bool:
    from pypdf import PdfReader

    leitor = PdfReader(str(pdf_path))
    total = len(leitor.pages)
    ok = True

    print("\nVerificação do PDF")
    print("  páginas: %d (esperado: %d)" % (total, esperado))
    ok &= total == esperado

    tamanhos = {(round(float(p.mediabox.width), 1), round(float(p.mediabox.height), 1))
                for p in leitor.pages}
    print("  dimensões (pt): %s" % tamanhos)
    ok &= all(abs(w - 595.2) < 2 and abs(h - 841.9) < 2 for w, h in tamanhos)

    vazias = []
    sem_texto = []
    imagens = 0
    for i, p in enumerate(leitor.pages, start=1):
        texto = (p.extract_text() or "").strip()
        if len(texto) < 25:
            sem_texto.append(i)
        if not texto:
            vazias.append(i)
        imagens += len(p.images)

    print("  imagens raster embutidas: %d (gráficos vetoriais quando 0)" % imagens)
    if sem_texto:
        print("  [ATENÇÃO] páginas com pouco texto: %s" % sem_texto)
    else:
        print("  [OK] todas as páginas possuem conteúdo textual")
    ok &= not vazias

    primeira = (leitor.pages[0].extract_text() or "")[:80].replace("\n", " · ")
    ultima = (leitor.pages[-1].extract_text() or "")[:80].replace("\n", " · ")
    print("  página 1: %s" % primeira)
    print("  página %d: %s" % (total, ultima))

    return ok


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--sem-pdf", action="store_true", help="apenas monta o HTML")
    ap.add_argument("--html-saida", default=str(HTML_SAIDA))
    ap.add_argument("--pdf-saida", default=str(PDF_SAIDA))
    args = ap.parse_args()

    html_path = montar_html()
    if args.html_saida != str(HTML_SAIDA):
        destino = Path(args.html_saida)
        destino.write_text(html_path.read_text(encoding="utf-8"), encoding="utf-8")
        html_path = destino

    if args.sem_pdf:
        return 0

    pdf_path = Path(args.pdf_saida)
    diagnostico = gerar_pdf(html_path, pdf_path)
    (OUTPUT / "diagnostico-paginacao.json").write_text(
        json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = verificar_pdf(pdf_path, esperado=len(diagnostico))
    print("\nResultado da geração: %s" % ("OK" if ok else "REVISAR"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
