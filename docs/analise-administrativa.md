# Análise administrativa — Inclusão digital na América do Sul

**Projeto:** Inclusão Digital: uma análise comparativa da evolução do acesso à Internet no Brasil e em países da América do Sul
**Disciplina:** Tecnologia da Informação e Comunicação Aplicada à Administração
**Indicador:** `IT.NET.USER.ZS` — Indivíduos que usam a Internet (% da população)
**Fonte:** Banco Mundial, World Development Indicators (WDI), base primária da ITU
**Recorte:** Brasil, Argentina, Chile e Uruguai — 2000 a 2024 (25 anos, sem lacunas)
**Coleta:** 17/11/2026, 18:00 UTC (API atualizada em 11/11/2026)

---

## 1. Resumo executivo

Entre 2000 e 2024, os quatro países deixaram de ter o acesso à Internet como privilégio de minorias e passaram a operar com cobertura próxima da universalização. O Brasil saiu de 2,87% para 84,46% da população (+81,59 pontos percentuais); a Argentina, de 7,04% para 89,67% (+82,63 pp); o Chile, de 16,60% para 95,59% (+78,99 pp); e o Uruguai, de 10,54% para 91,99% (+81,45 pp).

A leitura administrativa desse movimento tem duas consequências práticas. A primeira é que o problema dominante mudou de natureza: durante a maior parte do período, a questão era **conectar quem não estava conectado**; em 2024, com os quatro países acima de 84%, a questão passa a ser **qualificar o uso, integrar canais e atender com equidade a parcela que ainda está fora**. A segunda é que os ritmos se desaceleraram de forma generalizada, o que reduz o retorno esperado de estratégias baseadas apenas em aquisição de novos usuários.

Em 2024, o Brasil permanece 7,95 pp abaixo da média dos três países vizinhos (84,46% contra 92,42%) e apresenta a menor média do período (47,39%). O Chile lidera em 19 dos 25 anos analisados; o Brasil não ocupa a primeira posição em nenhum ano. A conclusão não é de fracasso — o crescimento absoluto brasileiro é o segundo maior do grupo —, mas de **posição relativa**: o país partiu de uma base muito baixa e, embora tenha crescido em ritmo acelerado, não fechou a distância em relação aos vizinhos.

---

## 2. Problema administrativo e recorte

A pergunta que orienta este documento é de natureza gerencial, não apenas estatística: **o que a trajetória de cobertura de Internet informa a decisões de planejamento, operação e investimento em organizações que atuam nesses mercados?**

Para responder, adotou-se um recorte deliberadamente restrito:

| Elemento | Definição |
|---|---|
| Fonte | Banco Mundial — World Development Indicators (WDI), dataset 2, série compilada a partir da ITU |
| Indicador | `IT.NET.USER.ZS` — indivíduos que usaram a Internet nos últimos três meses, em % da população total |
| Países | Brasil (BRA), Argentina (ARG), Chile (CHL) e Uruguai (URY) |
| Período | 2000–2024, comum aos quatro países e sem lacunas |
| Frequência | Anual |
| Tratamento | Valores preservados como publicados; ausências mantidas como ausentes, sem interpolação e sem zeros artificiais |
| Validação | Script de auditoria e duas coletas independentes (Python e PowerShell) com resultado idêntico |

O período começa em 2000 porque é o primeiro ano com observação para os quatro países simultaneamente. Anos anteriores existem na base, mas com lacunas (Argentina e Chile sem 1991; Uruguai sem 1991–1993), o que impediria comparações diretas. O Anexo B do relatório apresenta a série completa de 1990 a 2024 apenas para contexto histórico.

**Cuidado de interpretação que atravessa todo o documento:** pontos percentuais não são variação percentual. O Brasil cresceu 81,59 pontos percentuais entre 2000 e 2024, o que corresponde a aproximadamente 2.842% de variação relativa, porque a base inicial era de apenas 2,87%. As duas leituras estão corretas, mas respondem a perguntas diferentes: a primeira mede expansão absoluta da cobertura; a segunda, o esforço proporcional a partir do ponto de partida.

---

## 3. Diagnóstico comparativo

### 3.1 Nível e evolução

| País | 2000 | 2010 | 2020 | 2024 | Δ pp (2000–2024) | Δ relativa | Média 2000–2024 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Brasil | 2,87% | 40,65% | 81,34% | 84,46% | +81,59 pp | +2.842% | 47,39% |
| Argentina | 7,04% | 45,00% | 85,51% | 89,67% | +82,63 pp | +1.174% | 50,79% |
| Chile | 16,60% | 45,00% | 87,46% | 95,59% | +78,99 pp | +476% | 57,43% |
| Uruguai | 10,54% | 46,40% | 85,47% | 91,99% | +81,45 pp | +773% | 52,53% |
| **Média dos três vizinhos** | **11,39%** | **45,47%** | **86,15%** | **92,42%** | **+81,02 pp** | — | — |

Fonte: Banco Mundial (WDI). Elaboração própria.

Três fatos se destacam:

1. **Convergência parcial.** Em 2000, a distância entre o maior e o menor percentual era de 13,73 pp; em 2010, caiu para 5,75 pp. A aproximação, porém, não se manteve: em 2016 a amplitude chegou a 22,69 pp e, em 2024, ficou em 11,13 pp.
2. **Ordem de chegada diferente da ordem de partida.** Em termos relativos, o Brasil lidera (+2.842%), seguido de Argentina (+1.174%), Uruguai (+773%) e Chile (+476%). Em pontos percentuais, a Argentina lidera (+82,63 pp). A diferença entre as duas ordens é efeito matemático da base inicial, não de desempenho superior de um país sobre os outros.
3. **Patamar final elevado e relativamente homogêneo.** Todos os países terminaram o período acima de 84%, o que caracteriza mercados maduros em cobertura e desloca a disputa para qualidade, custo e intensidade de uso.

### 3.2 Ritmo e saturação

A média anual de variação em pontos percentuais revela três fases:

| Subperíodo | Brasil | Argentina | Chile | Uruguai |
|---|---:|---:|---:|---:|
| 2000–2009 | +4,04 pp/ano | +3,00 pp/ano | +2,77 pp/ano | +3,47 pp/ano |
| 2010–2019 | +3,70 pp/ano | +3,88 pp/ano | +4,45 pp/ano | +4,11 pp/ano |
| 2020–2024 | +0,78 pp/ano | +1,04 pp/ano | +2,03 pp/ano | +1,63 pp/ano |

Fonte: Banco Mundial (WDI). Média anual calculada entre o primeiro e o último ano de cada subperíodo. Elaboração própria.

Na primeira fase, o Brasil cresce no ritmo mais intenso do grupo (4,04 pp/ano). Na segunda, perde a dianteira para Chile e Uruguai e cai para 3,70 pp/ano. Na terceira, desacelera para 0,78 pp/ano — o menor avanço anual entre os quatro países. Essa inversão de liderança é o achado de maior consequência prática: **o país que comandou a expansão no início do período é o que apresenta menor dinamismo no fim**.

A desaceleração é esperada quando a cobertura se aproxima do limite populacional: cada ponto percentual adicional exige alcançar segmentos de menor renda, menor escolaridade ou maior dispersão territorial. O dado, porém, não permite atribuir causalidade — a série não contém preço, velocidade, qualidade de conexão, cobertura de rede ou renda. A leitura possível é descritiva: o ritmo caiu, e caiu mais no Brasil.

### 3.3 Posição relativa do Brasil

| Comparação | País em 2024 | Diferença em 2024 (Brasil − país) | Diferença máxima na série | Diferença mínima na série |
|---|---:|---:|---:|---:|
| Brasil − Argentina | 89,67% | −5,20 pp | +7,25 pp (2006) | −10,15 pp (2014) |
| Brasil − Chile | 95,59% | −11,13 pp | −2,34 pp (2009) | −22,69 pp (2016) |
| Brasil − Uruguai | 91,99% | −7,53 pp | +2,01 pp (2004) | −10,29 pp (2018) |

Fonte: Banco Mundial (WDI). Diferenças em pontos percentuais. Elaboração própria.

O Brasil nunca liderou o grupo, mas não esteve sempre atrás de todos: superou a Argentina entre 2003 e 2009 (máximo de +7,25 pp em 2006) e o Uruguai em 2004 e 2005. Frente ao Chile, a melhor posição foi −2,34 pp em 2009. A distância em relação à média dos três países caiu de −8,52 pp em 2000 para +0,10 pp em 2009, recuou para −4,82 pp em 2010 e voltou a −7,95 pp em 2024. Ou seja: houve aproximação na primeira década e afastamento relativo na segunda, movimento compatível com a desaceleração brasileira descrita em 3.2.

O Chile lidera em 19 dos 25 anos; o Uruguai, em 3 (2008–2010); a Argentina, em 3 (2012–2014). Não há ano de liderança brasileira.

---

## 4. Implicações administrativas

### 4.1 Planejamento estratégico e definição de metas

Com cobertura acima de 84% nos quatro países, metas formuladas apenas como “número de novos usuários” tendem a se tornar progressivamente mais difíceis e caras de atingir. O dado mais útil ao planejamento deixa de ser o nível e passa a ser a **derivada**: o ritmo de crescimento.

Consequência prática: organizações que operam nesses mercados devem separar metas de **expansão** (alcance de não usuários) de metas de **profundidade** (frequência de uso, tempo de permanência, transações por cliente). A segunda categoria passa a concentrar a maior parte do retorno marginal.

### 4.2 Transformação digital e desenho de canais

O patamar elevado de cobertura sustenta a migração de processos para canais digitais, mas não a garante. O indicador mede acesso, não adoção de serviços específicos. Ele funciona como **condição de contorno**: autoriza o desenho de jornadas digitais, mas não assegura que elas serão usadas.

A comparação regional oferece um critério de priorização: o Chile, com 95,59% em 2024, oferece ambiente mais favorável a jornadas exclusivamente digitais do que o Brasil, com 84,46%. A diferença de 11,13 pp não é trivial quando se considera o custo de manter canais paralelos (telefone, agência física, atendimento presencial) para atender quem não está plenamente conectado.

### 4.3 Comércio eletrônico e marketing digital

A expansão da base de usuários amplia o mercado endereçável de canais digitais. Com mais de 8 em cada 10 habitantes conectados nos quatro países, o limite de crescimento deixa de estar na quantidade de pessoas alcançáveis e passa a estar na **conversão** e na **retenção**.

Para marketing, isso desloca o esforço de aquisição de audiência para segmentação, personalização e mensuração. Para comércio eletrônico, desloca o esforço de logística de alcance para logística de última milha, atendimento e confiança transacional.

### 4.4 Sistemas de informação, dados e Business Intelligence

O trabalho em si é um exercício do encadeamento de BI em escala reduzida: identificação da fonte (API do Banco Mundial), extração por script, tratamento e padronização, cálculo de indicadores, apresentação em painel e relatório. A qualidade do resultado depende menos da ferramenta escolhida e mais da consistência das etapas anteriores.

Três decisões de governança de dados adotadas aqui são transferíveis a qualquer projeto administrativo:

- **Registro de proveniência:** data de coleta, indicador, código, dataset e fonte primária documentados na própria base.
- **Preservação de ausências:** anos sem observação permanecem ausentes; não se converte ausência em zero nem se interpola.
- **Reprodutibilidade:** duas implementações independentes de coleta e um script de auditoria que recalcula todas as métricas publicadas.

---

## 5. Riscos, limitações e cuidados de interpretação

| Limitação | Efeito sobre a conclusão | Mitigação adotada |
|---|---|---|
| Indicador de acesso, não de qualidade | Não mede velocidade, estabilidade ou custo da conexão | Escopo declarado; conclusões restritas a cobertura |
| Agregação nacional | Esconde desigualdades regionais, de renda e de território | Explicitado como limitação; recomenda-se desagregação futura |
| Série anual compilada por terceiro | Pode refletir revisões metodológicas da fonte primária | Valores preservados como publicados; data de acesso registrada |
| Ausência de variáveis explicativas | Impede inferência causal | Análise descritiva; nenhuma relação causal afirmada |
| Comparação entre bases iniciais distintas | Favorece leituras equivocadas de variação relativa | Distinção explícita entre pp e variação relativa em todo o material |
| Mudanças de instrumento de coleta | Altas ou quedas anuais isoladas podem refletir revisão, não comportamento | Eventos extremos comentados com cautela no relatório |

---

## 6. Recomendações priorizadas

| Prioridade | Recomendação | Indicador de acompanhamento |
|---|---|---|
| 1 | Tratar o Brasil como mercado de **retenção e profundidade**, não de aquisição em massa | Transações por usuário, frequência de uso, custo de atendimento por canal |
| 2 | Manter canais assistidos para a parcela não coberta, dimensionados pela distância à média regional | Percentual de atendimentos em canais presenciais/telefônicos |
| 3 | Usar a diferença de 11,13 pp em relação ao Chile como referência de maturidade digital, não como meta de cópia | Índice interno de digitalização de jornadas |
| 4 | Incorporar indicadores complementares (qualidade, custo, habilidades digitais) ao painel | Série própria com periodicidade definida |
| 5 | Desagregar dados por região e faixa de renda para orientar decisões locais | Cobertura por UF/região e por decil de renda |
| 6 | Institucionalizar a rotina de coleta e auditoria | Execução mensal do pipeline com registro de versão |

As recomendações 1 e 2 derivam diretamente da desaceleração brasileira (0,78 pp/ano em 2020–2024) e da posição relativa do país (−7,95 pp em relação à média dos três vizinhos). As recomendações 3 a 6 dependem de dados que este estudo não cobre e devem ser tratadas como agenda de continuidade.

---

<!-- quebra-de-pagina -->

## 7. Governança e reprodutibilidade

O projeto foi construído para que qualquer pessoa possa refazer o caminho e obter os mesmos números:

1. `scripts/fetch_data.py` consulta a API oficial do Banco Mundial e grava `data/internet_users.json`, `data/internet_users.csv` e o espelho `data/internet_users.js`.
2. `scripts/fetch_data.ps1` implementa a mesma coleta de forma independente; as duas execuções produziram séries idênticas.
3. `scripts/validate.py` audita a base (chaves, ordenação, faixa 0–100, duplicidades, lacunas, coerência entre JSON/CSV/JS) e recalcula todas as métricas divulgadas, conferindo se os valores aparecem nos artefatos publicados.
4. `scripts/build_report.py` monta o relatório autocontido e gera o PDF A4 com gráficos vetoriais.

Registro da coleta: **17/11/2026, 18:00 UTC**. API atualizada em **11/11/2026**. Total: **135 observações** (1990–2024), sendo **100 observações** no período de análise (4 países × 25 anos).

---

## 8. Conclusão

A inclusão digital na América do Sul, medida pelo acesso à Internet, avançou de forma inequívoca entre 2000 e 2024. O Brasil foi um dos protagonistas desse avanço em termos absolutos, mas não sustentou o ritmo: cresceu mais rápido que os vizinhos na primeira década e mais devagar na última, terminando o período abaixo da média regional e com a menor média histórica do grupo.

Para a Administração, o aprendizado central é que **a variável crítica mudou de natureza**. Enquanto a cobertura crescia em ritmo acelerado, o desafio era alcançar novos usuários; com a desaceleração, o desafio passa a ser qualificar o uso, integrar canais, elevar a produtividade e atender com equidade a parcela que ainda não está plenamente incluída. Decisões de investimento em plataformas digitais, desenho de canais e segmentação de mercado devem incorporar essa mudança de regime.

Do ponto de vista metodológico, o estudo demonstrou que é possível construir um diagnóstico comparativo consistente com dados públicos, sem custo de coleta primária e com rastreabilidade completa: a fonte é oficial, a extração é reprodutível por script, o tratamento preserva as ausências e os cálculos são verificáveis. O encadeamento adotado — API, tratamento, indicadores, visualização e interpretação — é o mesmo de um projeto de Business Intelligence.

Como continuidade, sugere-se incorporar indicadores de qualidade de conexão, custo e habilidades digitais; desagregar os dados por renda e território; e ampliar a comparação para outros países da região. Essas extensões permitiriam testar hipóteses que este estudo, por sua natureza descritiva, apenas delimita.

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

*Documento de apoio ao relatório `output/relatorio-inclusao-digital.pdf`. Os valores aqui reproduzidos são os mesmos auditados por `scripts/validate.py` e apresentados no painel `index.html`.*
