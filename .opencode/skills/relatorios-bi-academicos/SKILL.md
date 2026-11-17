---
name: relatorios-bi-academicos
description: Diretrizes permanentes para produzir relatórios acadêmicos com Business Intelligence, dashboards HTML e PDF A4. Use sempre que a tarefa envolver coleta de dados públicos, análise comparativa, gráficos de linhas com múltiplas séries, dashboard responsivo ou relatório acadêmico em PDF com identidade visual profissional.
---

# Skill: Relatórios Acadêmicos com Business Intelligence

Esta Skill define o padrão visual, analítico e textual a ser seguido em **todos** os artefatos
gerados (dashboard HTML, relatório HTML e relatório PDF). As regras são normativas: em caso de
dúvida, prevaleça o que está descrito aqui.

---

## 1. Identidade visual

### 1.1 Paleta oficial

| Papel | Token | Hex |
|---|---|---|
| Cor principal (séries, títulos, links) | `--azul` | `#1B4F9C` |
| Azul profundo (cabeçalhos, capa) | `--azul-escuro` | `#0F2C57` |
| Azul de apoio (faixas, realces) | `--azul-claro` | `#EAF1FB` |
| Complementar 1 | `--rosa` | `#C2185B` |
| Complementar 2 | `--verde` | `#1E7A45` |
| Complementar 3 | `--preto` | `#111418` |
| Texto corrido | `--texto` | `#24292F` |
| Texto secundário | `--texto-fraco` | `#5B6672` |
| Grade / bordas | `--grade` | `#E4E8EE` |
| Fundo | `--branco` | `#FFFFFF` |

### 1.2 Uso da cor

- O **branco** é sempre o fundo dominante. Nunca usar fundos escuros em páginas de conteúdo.
- O **azul** é a cor institucional: títulos, filetes, cabeçalhos de tabela, séries principais.
- **Rosa**, **verde** e **preto** são complementares e servem para distinguir séries e destacar
  achados pontuais. Não transformar a complementar em cor dominante.
- Cada série de dados tem cor fixa e exclusiva em todos os gráficos do projeto. A mesma variável
  nunca muda de cor entre gráficos, páginas ou artefatos.
- Evitar: gradientes decorativos, sombras fortes, ícones ilustrativos, emojis, texturas, marca d'água.

### 1.3 Tipografia

- Títulos: família sem serifa (Segoe UI, Inter, system-ui), pesos 600/700, azul escuro.
- Corpo (PDF acadêmico): família serifada legível (Cambria, Georgia, serif), 10,5–11 pt,
  `line-height` 1,5–1,6, texto **justificado** com `hyphens: auto`.
- Corpo (dashboard): sans-serif 16 px, `line-height` 1,7, alinhamento à esquerda, largura máxima
  de 72 caracteres por linha.
- Números em tabelas e eixos: `font-variant-numeric: tabular-nums`.
- Escala hierárquica: H1 20–22 pt · H2 15–16 pt · H3 12,5–13 pt · corpo 10,5 pt · legendas 9 pt.
- Não usar mais de duas famílias tipográficas por artefato.

### 1.4 Espaçamento e composição

- Respiro generoso: margens A4 de 22 mm (topo), 20 mm (laterais), 18 mm (base).
- Entre seções: 18–26 px; entre parágrafo e gráfico: 12–16 px; entre título e texto: 6–8 px.
- Máximo de 2 níveis de destaque por página; evitar caixas coloridas em excesso.
- Aparência acadêmica, sóbria, minimalista. Menos decoração, mais hierarquia.

---

## 2. Padrão obrigatório dos gráficos

Todos os gráficos seguem o modelo de **linhas múltiplas comparativas**:

1. **Tipo**: gráfico de linhas (`line`), uma linha por série, quatro séries no gráfico principal.
2. **Marcadores**: circulares, preenchidos com a cor da série, borda branca de 1,5–2 px,
   raio 3,5–4,5 px (PDF) — sempre visíveis, nunca omitidos.
3. **Espessura da linha**: 2–2,5 px (tela), 2 pt (impressão). Nunca usar linhas tracejadas para
   séries principais (reservar tracejado para médias e referências).
4. **Fundo**: branco puro, sem sombra e sem gradiente.
5. **Grade**: horizontal apenas, cor `#E4E8EE`, 1 px, atrás das séries. Grade vertical desativada
   (exceção: linhas verticais de referência em marcos históricos, muito discretas).
6. **Eixos**:
   - X: anos, sem rótulo redundante, espaçamento automático legível (evitar sobreposição).
   - Y: percentuais, começando em 0, com sufixo `%` e unidade explicitada.
   - Escala adequada ao intervalo real dos dados; nunca truncar o eixo de modo a exagerar diferenças.
7. **Legenda**: centralizada **abaixo** do gráfico, horizontal, marcadores circulares, sem caixa.
8. **Título**: acima do gráfico, com numeração (`Gráfico 1 — ...`). Subtítulo opcional indicando
   período e países.
9. **Fonte**: nota obrigatória sob o gráfico, 8,5–9 pt, cor `--texto-fraco`:
   `Fonte: ... Elaboração própria.`
10. **Lacunas de dados**: `spanGaps: false`. Nunca interpolar, nunca preencher com zero, nunca
    conectar pontos separados por anos ausentes.
11. **Acessibilidade**: contraste mínimo 3:1 entre linha e fundo; legenda textual além da cor
    (nome da série sempre escrito).
12. **Impressão**: renderizar em SVG ou em canvas com densidade ≥ 3× antes de gerar o PDF.

---

## 3. Tabelas

- Cabeçalho com fundo `--azul-claro`, texto `--azul-escuro`, peso 600, borda superior e inferior
  de 1 px em `--azul`.
- Linhas zebradas discretíssimas (`#FAFBFC`) ou apenas filetes horizontais de 1 px.
- Números alinhados à direita e com o mesmo número de casas decimais na coluna.
- Título acima (`Tabela 1 — ...`) e fonte abaixo, no mesmo padrão dos gráficos.
- Nunca quebrar uma linha da tabela entre duas páginas.

---

## 4. Regras textuais e analíticas

- Linguagem acadêmica natural, objetiva, em terceira pessoa ou primeira do plural.
- Toda afirmação quantitativa deve citar o valor, o ano e a fonte.
- **Separar explicitamente** o que é resultado observado do que é interpretação
  ("observa-se que..." vs. "isso sugere que...").
- Não afirmar causalidade sem evidência. Usar "associa-se", "coincide com", "é compatível com".
- Não inventar dados, autores, obras ou referências. Toda referência deve ser verificável.
- Diferenciar **pontos percentuais** (diferença aritmética entre percentuais) de
  **variação percentual relativa** ((final − inicial) / inicial × 100).
- Apresentar sempre as limitações metodológicas do indicador utilizado.
- Estrutura padrão de análise de gráfico: (a) o que o gráfico mostra; (b) tendência geral;
  (c) comparação entre séries; (d) pontos de inflexão; (e) leitura interpretativa.

---

## 5. Integridade de dados

1. Coletar da fonte oficial, registrar endpoint, data/hora da coleta e versão do dataset.
2. Preservar os valores originais sem arredondar na base; arredondar apenas na apresentação.
3. Registrar o período comum entre as séries e usá-lo nas comparações.
4. Dados ausentes permanecem ausentes (`null` / linha vazia). Jamais zero, jamais interpolação.
5. Cálculos devem ser reprodutíveis por script ou função documentada.
6. Recalcular toda métrica citada no texto a partir da base, nunca "de cabeça".

---

## 6. Relatório PDF (A4)

- Formato A4 (210 × 297 mm), margens conforme 1.4, `@page { size: A4; margin: 0 }`.
- Capa: título, subtítulo, disciplina, campos editáveis (aluno, instituição), cidade e ano.
- Sumário com números de página reais e conferidos com a paginação final.
- Cabeçalho discreto (título curto + filete azul) e rodapé com paginação.
- Numeração de páginas: capa sem número; páginas seguintes numeradas no rodapé.
- Corpo justificado, títulos hierarquizados, tabelas e gráficos com legenda e fonte.
- Nenhuma página em branco, nenhum elemento cortado, nenhum texto órfão de título.
- PDF gerado por Chromium/Playwright a partir de HTML+CSS de impressão, com os gráficos já
  renderizados. Verificar o PDF página a página após a geração.

---

## 7. Checklist final obrigatório

- [ ] Paleta e tipografia aplicadas de forma consistente nos três artefatos.
- [ ] Mesma cor para a mesma série em todos os gráficos.
- [ ] Valores dos gráficos conferidos contra a base original.
- [ ] Período comum declarado e utilizado.
- [ ] Legenda abaixo, marcadores circulares, grade horizontal discreta, fundo branco.
- [ ] Fonte e nota de elaboração sob cada gráfico e tabela.
- [ ] Pontos percentuais e variação percentual usados corretamente.
- [ ] Limitações metodológicas apresentadas.
- [ ] Referências com links verificáveis e testados.
- [ ] PDF conferido página a página (sem cortes, sem páginas vazias, sumário correto).
