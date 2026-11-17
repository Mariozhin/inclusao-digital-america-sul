# INCLUSÃO DIGITAL: UMA ANÁLISE COMPARATIVA DA EVOLUÇÃO DO ACESSO À INTERNET NO BRASIL E EM PAÍSES DA AMÉRICA DO SUL

**Recorte temporal: 2000–2024**

Projeto acadêmico da disciplina *Tecnologia da Informação e Comunicação Aplicada à Administração*. Coleta dados oficiais do Banco Mundial via API, audita a base, calcula indicadores e entrega três produtos: um painel interativo, um relatório em PDF e uma análise administrativa em Markdown.

---

## Resultados principais

Indicador `IT.NET.USER.ZS` — indivíduos que usam a Internet (% da população). Período 2000–2024, comum aos quatro países e sem lacunas.

| País | 2000 | 2024 | Δ pp | Δ relativa | Média do período |
|---|---:|---:|---:|---:|---:|
| Brasil | 2,87% | 84,46% | +81,59 pp | +2.842% | 47,39% |
| Argentina | 7,04% | 89,67% | +82,63 pp | +1.174% | 50,79% |
| Chile | 16,60% | 95,59% | +78,99 pp | +476% | 57,43% |
| Uruguai | 10,54% | 91,99% | +81,45 pp | +773% | 52,53% |

- O Brasil cresceu 81,59 pontos percentuais, mas permaneceu **7,95 pp abaixo da média** dos três vizinhos em 2024 (84,46% contra 92,42%) e registrou a **menor média do período**.
- O Chile liderou em **19 dos 25 anos**; o Brasil não ocupou a primeira posição em nenhum ano.
- O ritmo brasileiro caiu de **4,04 pp/ano** (2000–2009) para **0,78 pp/ano** (2020–2024) — a maior desaceleração do grupo.
- **Pontos percentuais não são variação percentual.** O Brasil cresceu 81,59 pp, o que equivale a +2.842% porque a base inicial era de apenas 2,87%.

---

## O que está no repositório

| Caminho | Descrição |
|---|---|
| `index.html` | Painel interativo (Chart.js local, funciona offline e no GitHub Pages) |
| `output/relatorio-inclusao-digital.pdf` | Relatório acadêmico A4, 23 páginas, gráficos vetoriais |
| `output/relatorio-inclusao-digital.html` | Versão web autocontida do relatório |
| `docs/analise-administrativa.md` | Análise administrativa, implicações gerenciais e recomendações |
| `output/analise-administrativa.pdf` | Documento de análise em A4, 8 páginas, gerado a partir do Markdown |
| `data/internet_users.json` | Base canônica (135 observações, 1990–2024) |
| `data/internet_users.csv` | Mesma base em CSV |
| `data/internet_users.js` | Espelho para uso do painel em `file://` |
| `scripts/fetch_data.py` | Coleta canônica via API do Banco Mundial |
| `scripts/fetch_data.ps1` | Coleta independente em PowerShell (validação cruzada) |
| `scripts/validate.py` | Auditoria da base e recálculo das métricas publicadas |
| `scripts/build_report.py` | Monta o HTML autocontido e gera o PDF com Playwright |
| `scripts/build_doc_pdf.py` | Converte a análise administrativa (Markdown) em PDF A4 |
| `report/` | Template e estilos do relatório (páginas A4 fixas) |
| `assets/` | CSS, JavaScript do painel e renderizador SVG dos gráficos |
| `.opencode/skills/relatorios-bi-academicos/SKILL.md` | Skill reutilizável para relatórios BI acadêmicos |

---

## Como reproduzir

### Pré-requisitos

- Python 3.10 ou superior
- Google Chrome instalado (usado pelo Playwright para gerar o PDF)

```bash
pip install -r requirements.txt
```

### 1. Coletar os dados

```bash
python scripts/fetch_data.py
```

O script consulta a API oficial, pagina os resultados e grava `data/internet_users.json`, `.csv` e `.js`. Registra data de coleta, indicador, dataset e fonte primária na própria base.

> **Nota sobre a API:** a consulta multi-país em um único endpoint (`/country/BRA;ARG;CHL;URY/...`) é bloqueada pelo WAF do Banco Mundial em parte dos ambientes (HTTP 502). O script usa consultas equivalentes, uma por país, no mesmo endpoint oficial, e consolida os resultados. A consulta multi-país permanece documentada em `fonte.url_api_multipais`.

### 2. Auditar e recalcular

```bash
python scripts/validate.py --baseline caminho/para/coleta_anterior.json
```

Verifica chaves obrigatórias, ordenação, duplicidades, faixa 0–100, lacunas, coerência entre JSON/CSV/JS e recalculação das métricas. O parâmetro `--baseline` é opcional e compara duas coletas independentes. O resultado é gravado em `output/validacao.json`.

### 3. Gerar o relatório

```bash
python scripts/build_report.py
```

Monta `output/relatorio-inclusao-digital.html` (CSS, dados e JS embutidos), renderiza o PDF A4 com gráficos vetoriais e grava o diagnóstico de paginação em `output/diagnostico-paginacao.json`.

### 4. Gerar o PDF da análise administrativa

```bash
python scripts/build_doc_pdf.py
```

Converte `docs/analise-administrativa.md` em `output/analise-administrativa.pdf` (A4, 8 páginas), com cabeçalho, rodapé numerado e tabelas formatadas. Gera também a versão web `output/analise-administrativa.html`.

### 5. Abrir o painel

```bash
python -m http.server 8000
```

Acesse `http://localhost:8000/index.html`. O painel também funciona abrindo `index.html` diretamente (`file://`), pois os dados são carregados do espelho JavaScript e o Chart.js está vendorizado em `assets/js/vendor/chart.umd.js`.

---

## Metodologia e integridade

- **Fonte oficial:** Banco Mundial, World Development Indicators (dataset 2), série compilada a partir da ITU.
- **Sem imputação:** anos sem observação permanecem ausentes. Nenhum zero artificial, nenhuma interpolação.
- **Duas coletas independentes:** Python e PowerShell produziram séries idênticas.
- **Rastreabilidade:** data de coleta (17/11/2026, 18:00 UTC), atualização da API (11/11/2026) e URL do indicador registradas na base.
- **Números conferidos:** `scripts/validate.py` recalcula as métricas e verifica se os valores publicados aparecem no relatório, no painel e na análise administrativa.
- **Gráficos vetoriais no PDF:** o relatório usa um renderizador SVG próprio; não há capturas de tela rasterizadas.
- **Links das referências:** cinco dos seis endereços retornam HTTP 200 em verificação automatizada. A página `data.worldbank.org/indicator/IT.NET.USER.ZS` responde 403 a clientes automatizados por proteção anti-bot, mas abre normalmente em navegador; o endpoint oficial da API (`api.worldbank.org/v2`) responde 200.

### Limitações

O indicador mede **acesso**, não qualidade, velocidade, custo ou habilidades digitais. Os dados são agregados por país e escondem desigualdades regionais e de renda. A série não contém variáveis explicativas, de modo que o estudo é descritivo e não permite inferência causal.

---

## Publicação no GitHub

O projeto está pronto para publicação, mas **não foi publicado automaticamente**: o ambiente de execução não possui `git` nem `gh` instalados/autenticados. Para publicar:

```bash
git init
git add .
git commit -m "Projeto de inclusão digital na América do Sul"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/inclusao-digital-america-sul.git
git push -u origin main
```

Para publicar o painel no GitHub Pages: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `/ (root)`**. O painel ficará em `https://SEU-USUARIO.github.io/inclusao-digital-america-sul/`.

---

## Skill reutilizável

`.opencode/skills/relatorios-bi-academicos/SKILL.md` descreve o fluxo completo — paleta, especificação dos gráficos, regras de impressão A4, regras textuais e checklist de validação — para reutilização em outros relatórios de BI acadêmicos.

---

## Referências

INTERNATIONAL TELECOMMUNICATION UNION. **World Telecommunication/ICT Indicators Database**. Genebra: ITU, 2025. Disponível em: <https://www.itu.int/en/ITU-D/Statistics/Pages/publications/wtid.aspx>. Acesso em: 17 nov. 2026.

INTERNATIONAL TELECOMMUNICATION UNION. **Measuring digital development: Facts and Figures**. Genebra: ITU, 2025. Disponível em: <https://www.itu.int/en/ITU-D/Statistics/Pages/facts/default.aspx>. Acesso em: 17 nov. 2026.

LAUDON, K. C.; LAUDON, J. P. **Management Information Systems: Managing the Digital Firm**. 16. ed. Harlow: Pearson, 2020.

NÚCLEO DE INFORMAÇÃO E COORDENAÇÃO DO PONTO BR. **TIC Domicílios**. São Paulo: Cetic.br/NIC.br, 2025. Disponível em: <https://cetic.br/pt/pesquisa/domicilios/>. Acesso em: 17 nov. 2026.

WORLD BANK. **World Development Indicators** [base de dados]. Washington, DC: World Bank, 2026. Disponível em: <https://databank.worldbank.org/source/world-development-indicators>. Acesso em: 17 nov. 2026.

WORLD BANK. **Individuals using the Internet (% of population) — IT.NET.USER.ZS**. Washington, DC: World Bank, 2026. Disponível em: <https://data.worldbank.org/indicator/IT.NET.USER.ZS>. Acesso em: 17 nov. 2026.

WORLD BANK. **World Bank Open Data — API v2: developer documentation**. Washington, DC: World Bank, 2026. Disponível em: <https://datahelpdesk.worldbank.org/knowledgebase/articles/889392>. Acesso em: 17 nov. 2026.

---

**Dados:** © Banco Mundial, World Development Indicators (CC BY 4.0). **Uso:** acadêmico e educacional.
