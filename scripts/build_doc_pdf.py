#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_doc_pdf.py — converte docs/analise-administrativa.md em PDF A4.

Etapas
------
1. Lê o Markdown, separa o bloco de identificação (título + metadados) e converte
   o restante em HTML (títulos, parágrafos, listas, tabelas com alinhamento,
   ênfases, código e links), sem dependências externas de Markdown.
2. Monta um HTML autocontido com a identidade visual do projeto e o abre no Chrome
   via Playwright (canal "chrome", sem download de navegador).
3. Gera o PDF em A4 com cabeçalho e rodapé discretos, numeração "Página X de Y",
   parágrafos justificados e tabelas sem quebra no meio.
4. Verifica o resultado: dimensões, páginas com texto, ausência de imagens raster
   e ausência de texto além da área útil.

Uso:
    python scripts/build_doc_pdf.py [--md CAMINHO] [--pdf-saida CAMINHO]
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MD_PADRAO = RAIZ / "docs" / "analise-administrativa.md"
PDF_SAIDA = RAIZ / "output" / "analise-administrativa.pdf"
HTML_SAIDA = RAIZ / "output" / "analise-administrativa.html"

META_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.+)$")
H2_RE = re.compile(r"^(\d+)\.\s+(.+)$")
H3_RE = re.compile(r"^(\d+\.\d+)\s+(.+)$")
UL_RE = re.compile(r"^[-*]\s+(.+)$")
OL_RE = re.compile(r"^(\d+)\.\s+(.+)$")


# --------------------------------------------------------------------------
# Markdown -> HTML
# --------------------------------------------------------------------------
def inline(texto: str) -> str:
    """Converte ênfases, código e links de uma linha de Markdown."""
    t = html.escape(texto, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"&lt;(https?://[^\s&]+?)&gt;", r'<a href="\1">\1</a>', t)
    return t


def separar_cabecalho(linhas: list[str]) -> tuple[str, list[tuple[str, str]], int]:
    """Extrai o H1 e as linhas '**Rótulo:** valor' do início do documento."""
    titulo = ""
    meta: list[tuple[str, str]] = []
    i = 0
    while i < len(linhas) and not linhas[i].strip():
        i += 1
    if i < len(linhas) and linhas[i].startswith("# "):
        titulo = linhas[i][2:].strip()
        i += 1
    while i < len(linhas):
        linha = linhas[i].strip()
        if not linha:
            i += 1
            continue
        m = META_RE.match(linha)
        if m:
            meta.append((m.group(1).strip(), m.group(2).strip()))
            i += 1
            continue
        if linha == "---":
            i += 1
        break
    return titulo, meta, i


def alinhamentos(sep: str) -> list[str]:
    """Lê a linha separadora de uma tabela e devolve o alinhamento por coluna."""
    saida = []
    for celula in sep.strip().strip("|").split("|"):
        c = celula.strip()
        if c.startswith(":") and c.endswith(":"):
            saida.append("center")
        elif c.endswith(":"):
            saida.append("right")
        elif c.startswith(":"):
            saida.append("left")
        else:
            saida.append("")
    return saida


def celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def classe_align(align: str) -> str:
    return {"right": "num", "center": "centro"}.get(align, "")


def converter_corpo(linhas: list[str], inicio: int) -> str:
    blocos: list[str] = []
    i = inicio
    em_referencias = False
    lista_aberta: str | None = None
    paragrafo: list[str] = []

    def fechar_lista() -> None:
        nonlocal lista_aberta
        if lista_aberta:
            blocos.append("</%s>" % lista_aberta)
            lista_aberta = None

    def fechar_paragrafo() -> None:
        if paragrafo:
            texto = " ".join(p.strip() for p in paragrafo)
            if em_referencias:
                classe = ' class="ref"'
            elif texto.startswith(("Fonte:", "Fontes:")):
                classe = ' class="fonte"'
            else:
                classe = ""
            blocos.append("<p%s>%s</p>" % (classe, inline(texto)))
            paragrafo.clear()

    while i < len(linhas):
        linha = linhas[i]
        stripped = linha.strip()

        if not stripped:
            fechar_paragrafo()
            fechar_lista()
            i += 1
            continue

        # Quebra de página explícita, invisível na leitura do Markdown
        if stripped == "<!-- quebra-de-pagina -->":
            fechar_paragrafo()
            fechar_lista()
            blocos.append('<div class="quebra-pagina"></div>')
            i += 1
            continue

        # Tabela: linha com "|" seguida de separador
        if stripped.startswith("|") and i + 1 < len(linhas) and re.match(
                r"^\|?[\s:|-]+\|[\s:|-]*$", linhas[i + 1].strip()):
            fechar_paragrafo()
            fechar_lista()
            cab = celulas(stripped)
            aligns = alinhamentos(linhas[i + 1])
            i += 2
            corpo = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                corpo.append(celulas(linhas[i].strip()))
                i += 1
            ths = "".join(
                '<th class="%s">%s</th>' % (
                    classe_align(aligns[n] if n < len(aligns) else ""),
                    inline(c).replace("Δ ", "Δ&nbsp;"),
                )
                for n, c in enumerate(cab)
            )
            trs = []
            for linha_corpo in corpo:
                tds = "".join(
                    '<td class="%s">%s</td>' % (classe_align(aligns[n] if n < len(aligns) else ""), inline(c))
                    for n, c in enumerate(linha_corpo)
                )
                trs.append("<tr>%s</tr>" % tds)
            blocos.append(
                '<div class="tabela"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                % (ths, "".join(trs))
            )
            continue

        if stripped.startswith("#"):
            fechar_paragrafo()
            fechar_lista()
            nivel = len(stripped) - len(stripped.lstrip("#"))
            texto = stripped[nivel:].strip()
            if nivel == 2:
                em_referencias = texto.lower().startswith("refer")
                m = H2_RE.match(texto)
                if m:
                    blocos.append('<h2><span class="num">%s</span>%s</h2>' % (m.group(1), inline(m.group(2))))
                elif em_referencias:
                    blocos.append('<h2 class="referencias">%s</h2>' % inline(texto))
                else:
                    blocos.append("<h2>%s</h2>" % inline(texto))
            elif nivel == 3:
                m = H3_RE.match(texto)
                if m:
                    blocos.append('<h3><span class="num">%s</span>%s</h3>' % (m.group(1), inline(m.group(2))))
                else:
                    blocos.append("<h3>%s</h3>" % inline(texto))
            else:
                blocos.append("<h4>%s</h4>" % inline(texto))
            i += 1
            continue

        if re.match(r"^-{3,}$", stripped) or re.match(r"^\*{3,}$", stripped):
            fechar_paragrafo()
            fechar_lista()
            # Separadores antes de um novo capítulo são redundantes com a borda do h2.
            proximo = next(
                (l.strip() for l in linhas[i + 1:] if l.strip() and l.strip() != "<!-- quebra-de-pagina -->"),
                "",
            )
            if not proximo.startswith("#"):
                blocos.append('<hr class="divisor">')
            i += 1
            continue

        m = UL_RE.match(stripped)
        if m:
            fechar_paragrafo()
            if lista_aberta != "ul":
                fechar_lista()
                blocos.append("<ul>")
                lista_aberta = "ul"
            blocos.append("<li>%s</li>" % inline(m.group(1)))
            i += 1
            continue

        m = OL_RE.match(stripped)
        if m and not re.match(r"^\d+\.\d", stripped):
            fechar_paragrafo()
            if lista_aberta != "ol":
                fechar_lista()
                blocos.append("<ol>")
                lista_aberta = "ol"
            blocos.append("<li>%s</li>" % inline(m.group(2)))
            i += 1
            continue

        if stripped.startswith(">"):
            fechar_paragrafo()
            fechar_lista()
            blocos.append('<blockquote><p>%s</p></blockquote>' % inline(stripped.lstrip("> ")))
            i += 1
            continue

        paragrafo.append(stripped)
        i += 1

    fechar_paragrafo()
    fechar_lista()
    return "\n".join(blocos)


# --------------------------------------------------------------------------
# Template
# --------------------------------------------------------------------------
CSS = """
:root {
  --azul: #1B4F9C;
  --azul-escuro: #0F2C57;
  --azul-claro: #EAF1FB;
  --rosa: #C2185B;
  --verde: #1E7A45;
  --preto: #111418;
  --texto: #24292F;
  --texto-fraco: #5B6672;
  --grade: #E4E8EE;
  --sans: "Segoe UI", "Inter", system-ui, Arial, sans-serif;
  --serif: Cambria, Georgia, "Times New Roman", serif;
}

* { box-sizing: border-box; }

html, body { margin: 0; padding: 0; background: #FFFFFF; }

body {
  font-family: var(--serif);
  font-size: 10.5pt;
  line-height: 1.63;
  color: var(--texto);
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* ---------------------------------------------------------- abertura */
.abertura { margin: 0 0 11mm; }

.eyebrow {
  display: inline-block;
  font-family: var(--sans);
  font-size: 7.4pt;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--azul);
  border-left: 3px solid var(--azul);
  padding-left: 10px;
  margin-bottom: 6mm;
}

h1 {
  font-family: var(--sans);
  font-size: 27pt;
  line-height: 1.12;
  letter-spacing: -0.022em;
  font-weight: 700;
  color: var(--azul-escuro);
  margin: 0 0 4mm;
  max-width: 148mm;
}

.deck {
  font-family: var(--sans);
  font-size: 12.4pt;
  line-height: 1.5;
  color: var(--texto-fraco);
  margin: 0 0 7mm;
  max-width: 152mm;
}

.meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  column-gap: 10mm;
  row-gap: 3.2mm;
  margin: 0 0 7mm;
  padding: 5mm 0 0;
  border-top: 0.6pt solid var(--grade);
}

.meta dt {
  font-family: var(--sans);
  font-size: 6.9pt;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--azul);
  margin: 0 0 0.8mm;
}

.meta dd {
  font-family: var(--sans);
  font-size: 8.5pt;
  line-height: 1.4;
  color: var(--texto);
  margin: 0;
}

.meta code { font-size: 8pt; }

.rule {
  width: 26mm;
  height: 2.4pt;
  background: var(--rosa);
  border: 0;
  margin: 0;
}

/* ---------------------------------------------------------- títulos */
h2 {
  font-family: var(--sans);
  font-size: 15.5pt;
  line-height: 1.25;
  font-weight: 700;
  color: var(--azul-escuro);
  margin: 9mm 0 3.5mm;
  padding-bottom: 1.6mm;
  border-bottom: 0.7pt solid var(--grade);
  break-after: avoid;
  page-break-after: avoid;
}

h2:first-of-type { margin-top: 0; }

h2.referencias {
  break-before: page;
  page-break-before: always;
  margin-top: 0;
}

.quebra-pagina {
  break-after: page;
  page-break-after: always;
  height: 0;
}

h2 .num {
  color: var(--azul);
  font-weight: 700;
  margin-right: 2.6mm;
}

h2 .num::after { content: ""; }

h3 {
  font-family: var(--sans);
  font-size: 11.4pt;
  line-height: 1.35;
  font-weight: 700;
  color: var(--azul);
  margin: 6.5mm 0 2.2mm;
  break-after: avoid;
  page-break-after: avoid;
}

h3 .num { color: var(--rosa); margin-right: 2mm; }

h4 {
  font-family: var(--sans);
  font-size: 10pt;
  color: var(--azul-escuro);
  margin: 5mm 0 2mm;
}

/* ---------------------------------------------------------- texto */
p {
  margin: 0 0 3.4mm;
  text-align: justify;
  orphans: 3;
  widows: 3;
}

strong { color: var(--azul-escuro); font-weight: 700; }

em { font-style: italic; }

p.fonte {
  font-family: var(--sans);
  font-size: 7.9pt;
  line-height: 1.45;
  color: var(--texto-fraco);
  text-align: left;
  margin: -1.4mm 0 4.4mm;
}

a {
  color: var(--azul);
  text-decoration: none;
  border-bottom: 0.4pt solid rgba(27, 79, 156, 0.35);
  overflow-wrap: anywhere;
}

code {
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: 8.7pt;
  color: var(--azul);
  background: #F1F5FB;
  padding: 0.2mm 0.55mm;
  border-radius: 2px;
}

ul, ol {
  margin: 0 0 3.6mm;
  padding-left: 6mm;
}

li { margin: 0 0 1.4mm; }

ul li::marker { color: var(--azul); }
ol li::marker { color: var(--rosa); font-weight: 700; }

hr.divisor {
  border: 0;
  border-top: 0.6pt solid var(--grade);
  margin: 7mm 0;
}

blockquote {
  margin: 0 0 4mm;
  padding: 3mm 4mm;
  background: var(--azul-claro);
  border-left: 3pt solid var(--azul);
}

blockquote p { margin: 0; }

/* ---------------------------------------------------------- tabelas */
.tabela {
  margin: 3mm 0 5.5mm;
  break-inside: avoid;
  page-break-inside: avoid;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--sans);
  font-size: 8.3pt;
  line-height: 1.4;
}

thead { display: table-header-group; }

th {
  background: var(--azul-claro);
  color: var(--azul-escuro);
  font-size: 6.9pt;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  text-align: left;
  padding: 2.2mm 2.2mm;
  border-bottom: 1pt solid var(--azul);
  vertical-align: bottom;
  hyphens: none;
}

td {
  padding: 1.9mm 2.4mm;
  border-bottom: 0.5pt solid var(--grade);
  vertical-align: top;
  color: var(--texto);
}

tbody tr:nth-child(even) td { background: #FAFBFD; }

th.num, td.num { text-align: right; }
th.centro, td.centro { text-align: center; }

/* ---------------------------------------------------------- referências */
p.ref {
  text-align: left;
  padding-left: 6mm;
  text-indent: -6mm;
  margin-bottom: 3.2mm;
  font-size: 9.9pt;
  line-height: 1.5;
}

/* ---------------------------------------------------------- fim */
.nota-final {
  margin-top: 7mm;
  padding-top: 3mm;
  border-top: 0.6pt solid var(--grade);
  font-size: 8.6pt;
  color: var(--texto-fraco);
  font-style: italic;
  text-align: left;
}
"""


def montar_html(md: Path) -> str:
    linhas = md.read_text(encoding="utf-8").splitlines()
    titulo, meta, inicio = separar_cabecalho(linhas)
    corpo = converter_corpo(linhas, inicio)

    # Título: "Análise administrativa — Inclusão digital na América do Sul"
    partes = [p.strip() for p in titulo.split("—")]
    titulo_curto = partes[0] if partes else titulo
    subtitulo = partes[1] if len(partes) > 1 else ""

    meta_html = "".join(
        "<div><dt>%s</dt><dd>%s</dd></div>" % (html.escape(rot), inline(val))
        for rot, val in meta
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{html.escape(titulo)}</title>
<style>{CSS}</style>
</head>
<body>
<header class="abertura">
  <span class="eyebrow">Documento de apoio · Análise administrativa</span>
  <h1>{html.escape(titulo_curto)}</h1>
  <p class="deck">{html.escape(subtitulo)} — implicações gerenciais da evolução do acesso à Internet no Brasil, Argentina, Chile e Uruguai (2000–2024)</p>
  <dl class="meta">{meta_html}</dl>
  <hr class="rule">
</header>
<main>
{corpo}
</main>
</body>
</html>
"""


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------
CABECALHO = """
<div style="width:100%;margin:0 22mm;font-family:'Segoe UI',Arial,sans-serif;font-size:7pt;
            letter-spacing:.07em;text-transform:uppercase;color:#7A8697;
            display:flex;justify-content:space-between;align-items:flex-end;
            border-bottom:.5px solid #DCE3ED;padding-bottom:2mm;box-sizing:border-box;">
  <span style="color:#0F2C57;font-weight:600;">Inclusão digital na América do Sul</span>
  <span>Análise administrativa</span>
</div>
"""

RODAPE = """
<div style="width:100%;margin:0 22mm;font-family:'Segoe UI',Arial,sans-serif;font-size:7pt;
            color:#7A8697;display:flex;justify-content:space-between;align-items:flex-start;
            border-top:.5px solid #DCE3ED;padding-top:2mm;box-sizing:border-box;">
  <span>Elaboração própria com dados do Banco Mundial (WDI) · Coleta 17/11/2026</span>
  <span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span>
</div>
"""


def gerar_pdf(html_path: Path, pdf_path: Path) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        try:
            navegador = pw.chromium.launch(channel="chrome", headless=True)
        except Exception as exc:  # noqa: BLE001
            raise SystemExit(
                "Não foi possível iniciar o Chrome via Playwright (channel='chrome'): %s" % exc
            )
        pagina = navegador.new_page(viewport={"width": 1240, "height": 1000})
        pagina.goto(html_path.as_uri(), wait_until="load")
        pagina.emulate_media(media="print")
        pagina.wait_for_timeout(400)

        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pagina.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template=CABECALHO,
            footer_template=RODAPE,
            margin={"top": "22mm", "bottom": "18mm", "left": "22mm", "right": "22mm"},
        )
        navegador.close()


def verificar_pdf(pdf_path: Path) -> bool:
    import pymupdf

    doc = pymupdf.open(pdf_path)
    largura, altura = doc[0].rect.width, doc[0].rect.height
    margem = 22 * 72 / 25.4
    limite_x = largura - margem + 2
    ok = True

    print("Verificação do PDF")
    print("  páginas: %d" % doc.page_count)
    print("  dimensões (pt): %.1f × %.1f" % (largura, altura))
    ok &= abs(largura - 595.2) < 2 and abs(altura - 841.9) < 2

    imagens = sum(len(p.get_images(full=True)) for p in doc)
    print("  imagens raster embutidas: %d" % imagens)
    ok &= imagens == 0

    vazias, excedidas = [], []
    for n, p in enumerate(doc, start=1):
        texto = (p.get_text() or "").strip()
        if len(texto) < 60:
            vazias.append(n)
        for bloco in p.get_text("blocks"):
            if bloco[2] > limite_x + 1:
                excedidas.append((n, round(bloco[2], 1)))
                break

    if vazias:
        print("  [ATENÇÃO] páginas com pouco texto: %s" % vazias)
        ok = False
    else:
        print("  [OK] todas as páginas possuem conteúdo textual")

    if excedidas:
        print("  [ATENÇÃO] texto além da área útil: %s" % excedidas)
        ok = False
    else:
        print("  [OK] nenhum texto excede a área útil")

    amostras = {
        1: "Resumo executivo",
        doc.page_count: "Documento de apoio",
    }
    for pag, trecho in amostras.items():
        texto = doc[pag - 1].get_text()
        if trecho not in texto:
            print("  [ATENÇÃO] página %d sem o trecho esperado: %r" % (pag, trecho))
            ok = False

    print("  página 1: %s" % doc[0].get_text().split("\n")[2][:70])
    return ok


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=str(MD_PADRAO))
    ap.add_argument("--pdf-saida", default=str(PDF_SAIDA))
    ap.add_argument("--sem-pdf", action="store_true")
    args = ap.parse_args()

    html_doc = montar_html(Path(args.md))
    HTML_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    HTML_SAIDA.write_text(html_doc, encoding="utf-8")
    print("HTML gerado: %s (%.0f KB)" % (HTML_SAIDA, len(html_doc.encode("utf-8")) / 1024))

    if args.sem_pdf:
        return 0

    pdf_path = Path(args.pdf_saida)
    gerar_pdf(HTML_SAIDA, pdf_path)
    print("PDF gerado: %s (%.0f KB)" % (pdf_path, pdf_path.stat().st_size / 1024))
    ok = verificar_pdf(pdf_path)
    print("\nResultado da geração: %s" % ("OK" if ok else "REVISAR"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
