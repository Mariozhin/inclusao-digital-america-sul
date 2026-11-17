/*
 * relatorio.js — preenche o relatório acadêmico com os dados coletados.
 *
 * Responsabilidades:
 *   - gerar os quatro gráficos em SVG vetorial (impressão nítida);
 *   - preencher as tabelas de resultados a partir da base;
 *   - numerar sumário e rodapés de forma consistente;
 *   - expor diagnosticarPaginas() para a auditoria de paginação.
 */
(function () {
  "use strict";

  var fmt2 = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var fmt0 = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });

  function pct(v) { return v === null || v === undefined ? "—" : fmt2.format(v) + "%"; }
  function pp(v) {
    if (v === null || v === undefined) return "—";
    return (v > 0 ? "+" : v < 0 ? "−" : "") + fmt2.format(Math.abs(v)) + " pp";
  }
  function sinalClasse(v) { return v === null ? "" : v < 0 ? "pp-neg" : "pp-pos"; }

  function td(tr, texto, classe) {
    var c = document.createElement("td");
    c.textContent = texto;
    if (classe) c.className = classe;
    tr.appendChild(c);
    return c;
  }

  function linha(tbody, rotulo, valores, opcoes) {
    var tr = document.createElement("tr");
    if (opcoes && opcoes.destaque) tr.className = "destaque";
    var th = document.createElement("td");
    th.textContent = rotulo;
    tr.appendChild(th);
    valores.forEach(function (v) {
      if (typeof v === "object" && v !== null) td(tr, v.texto, v.classe);
      else td(tr, v);
    });
    tbody.appendChild(tr);
    return tr;
  }

  function iniciar(ds) {
    var an = new Analytics(ds);
    var anos = ds.periodo.anos_analise;
    var ultimo = anos[anos.length - 1];
    var aud = an.auditar();

    // ---------------------------------------------------------- datas da base
    var fmtData = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
    var coleta = new Date(ds.coleta.data_utc);
    var coletaTxt = isNaN(coleta.getTime())
      ? ds.coleta.data_utc
      : fmtData.format(coleta) + " às " +
        String(coleta.getUTCHours()).padStart(2, "0") + ":" +
        String(coleta.getUTCMinutes()).padStart(2, "0") + " UTC";

    document.querySelectorAll("[data-coleta]").forEach(function (n) {
      n.textContent = coletaTxt;
    });
    document.querySelectorAll("[data-api-atualizada]").forEach(function (n) {
      n.textContent = ds.fonte.api_atualizada_em;
    });
    document.querySelectorAll("[data-observacoes]").forEach(function (n) {
      n.textContent = String(aud.observacoes);
    });
    document.querySelectorAll("[data-periodo]").forEach(function (n) {
      n.textContent = ds.periodo.analise.inicio + "–" + ds.periodo.analise.fim;
    });

    // -------------------------------------------------------------- gráfico 1
    SVGChart.linhas(document.getElementById("graf-1"), {
      largura: 900, altura: 430, anos: anos, puloAnos: 2,
      yMin: 0, yMax: 100, yPasso: 20, sufixo: "%",
      rotulo: "Evolução do uso da Internet no Brasil, Argentina, Chile e Uruguai, 2000 a 2024",
      series: ds.series.map(function (s) {
        return { nome: s.nome, cor: s.cor, valores: an.serie(s.codigo, anos) };
      })
    });

    // -------------------------------------------------------------- gráfico 2
    SVGChart.linhas(document.getElementById("graf-2"), {
      largura: 900, altura: 430, anos: anos, puloAnos: 2,
      yMin: 0, yMax: 100, yPasso: 20, sufixo: "%",
      rotulo: "Comparação entre o Brasil e a média de Argentina, Chile e Uruguai, 2000 a 2024",
      series: [
        { nome: "Brasil", cor: "#1B4F9C", valores: an.serie("BRA", anos) },
        { nome: "Média de Argentina, Chile e Uruguai", cor: "#C2185B",
          valores: an.mediaEstrangeiros(anos), tracejado: true }
      ]
    });

    // -------------------------------------------------------------- gráfico 3
    SVGChart.linhas(document.getElementById("graf-3"), {
      largura: 900, altura: 430, anos: anos, puloAnos: 2,
      yMin: -25, yMax: 10, yPasso: 5, sufixo: " pp", zero: true,
      rotulo: "Diferença, em pontos percentuais, entre o Brasil e cada um dos três países, 2000 a 2024",
      series: [
        { nome: "Brasil − Argentina", cor: "#C2185B", valores: an.diferencaBrasilPais("ARG", anos) },
        { nome: "Brasil − Chile", cor: "#1E7A45", valores: an.diferencaBrasilPais("CHL", anos) },
        { nome: "Brasil − Uruguai", cor: "#111418", valores: an.diferencaBrasilPais("URY", anos) }
      ]
    });

    // -------------------------------------------------------------- gráfico 4
    var anosCompletos = [];
    for (var a = ds.periodo.serie_completa.inicio; a <= ds.periodo.serie_completa.fim; a++) anosCompletos.push(a);
    SVGChart.linhas(document.getElementById("graf-4"), {
      largura: 900, altura: 430, anos: anosCompletos, puloAnos: 5,
      yMin: 0, yMax: 100, yPasso: 20, sufixo: "%",
      rotulo: "Série histórica completa de 1990 a 2024, com lacunas preservadas",
      series: ds.series.map(function (s) {
        return { nome: s.nome, cor: s.cor, valores: an.serie(s.codigo, anosCompletos) };
      })
    });

    // -------------------------------------------------------------- tabela 2
    var t2 = document.getElementById("tab-metricas");
    if (t2) {
      ds.series.forEach(function (s) {
        var m = an.metricasPais(s.codigo);
        linha(t2, s.nome, [
          pct(m.primeiroValor), pct(m.ultimoValor),
          { texto: pp(m.deltaPP), classe: "pp-pos" },
          fmt0.format(Math.round(m.variacaoRelativa)) + "%",
          pct(m.media)
        ], { destaque: s.codigo === "BRA" });
      });
      var iniMed = Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, anos[0]); }));
      var fimMed = Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, ultimo); }));
      var medMed = Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.metricasPais(c).media; }));
      linha(t2, "Média de ARG, CHL e URY", [pct(iniMed), pct(fimMed), pp(fimMed - iniMed), "—", pct(medMed)]);
    }

    // -------------------------------------------------------------- tabela 3
    var t3 = document.getElementById("tab-diferencas");
    if (t3) {
      Analytics.ESTRANGEIROS.forEach(function (c) {
        var d = an.diferencaBrasilPais(c, anos);
        var maior = d.indexOf(Math.max.apply(null, d));
        var menor = d.indexOf(Math.min.apply(null, d));
        linha(t3, "Brasil − " + an.info(c).nome, [
          pct(an.valor(c, ultimo)),
          { texto: pp(d[d.length - 1]), classe: sinalClasse(d[d.length - 1]) },
          { texto: pp(d[maior]) + " (" + anos[maior] + ")", classe: "pp-pos" },
          { texto: pp(d[menor]) + " (" + anos[menor] + ")", classe: "pp-neg" }
        ]);
      });
    }

    // -------------------------------------------------------------- tabela 4
    var t4 = document.getElementById("tab-subperiodos");
    if (t4) {
      an.subperiodos().forEach(function (bloco) {
        var valores = Analytics.PAISES.map(function (c) {
          var v = bloco[c].porAno;
          return { texto: pp(v).replace(" pp", "") + " pp/ano", classe: "pp-pos" };
        });
        linha(t4, bloco.inicio + "–" + bloco.fim, valores);
      });
    }

    // ------------------------------------------------- tabela 2 (anos selecionados)
    var tsel = document.getElementById("tab-selecionados");
    if (tsel) {
      var difsSel = an.diferencaBrasilMedia(anos);
      [2000, 2005, 2010, 2015, 2020, 2024].forEach(function (ano) {
        var i = anos.indexOf(ano);
        if (i < 0) return;
        var tr = document.createElement("tr");
        td(tr, String(ano));
        Analytics.PAISES.forEach(function (c) {
          var cel = td(tr, pct(an.valor(c, ano)));
          cel.style.color = an.info(c).cor;
        });
        td(tr, pct(Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, ano); }))));
        td(tr, pp(difsSel[i]), sinalClasse(difsSel[i]));
        tsel.appendChild(tr);
      });
    }

    // -------------------------------------------------------------- anexo A
    var tanexo = document.getElementById("tab-anual");    if (tanexo) {
      var difs = an.diferencaBrasilMedia(anos);
      anos.forEach(function (ano, i) {
        var tr = document.createElement("tr");
        td(tr, String(ano));
        Analytics.PAISES.forEach(function (c) {
          var cel = td(tr, pct(an.valor(c, ano)));
          cel.style.color = an.info(c).cor;
        });
        td(tr, pct(Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, ano); }))));
        td(tr, pp(difs[i]), sinalClasse(difs[i]));
        tanexo.appendChild(tr);
      });
    }

    // ------------------------------------------------------- sumário e folios
    document.querySelectorAll(".sumario-linha[data-sec]").forEach(function (linhaSum) {
      var alvo = document.querySelector('[data-destino="' + linhaSum.dataset.sec + '"]');
      var pag = alvo ? alvo.closest(".page") : null;
      var destino = linhaSum.querySelector(".pagina");
      if (destino && pag) destino.textContent = pag.dataset.page;
      if (alvo && pag) {
        var link = linhaSum.querySelector("a");
        if (link) link.setAttribute("href", "#pagina-" + pag.dataset.page);
      }
    });

    document.querySelectorAll(".page[data-page]").forEach(function (p) {
      var folio = p.querySelector(".folio");
      if (folio) folio.textContent = p.dataset.page;
    });

    // ------------------------------------------------------------- diagnóstico
    window.diagnosticarPaginas = function () {
      var sonda = document.createElement("div");
      sonda.style.cssText = "position:absolute;width:1mm;height:1mm;left:0;top:0";
      document.body.appendChild(sonda);
      var pxPerMm = sonda.getBoundingClientRect().width;
      document.body.removeChild(sonda);

      return Array.from(document.querySelectorAll(".page")).map(function (p) {
        var conteudo = p.querySelector(".page-conteudo");
        var pr = p.getBoundingClientRect();
        var limite = pr.bottom - 17 * pxPerMm;
        var pior = 0;
        if (conteudo) {
          Array.from(conteudo.children).forEach(function (ch) {
            var r = ch.getBoundingClientRect();
            if (r.bottom > limite) pior = Math.max(pior, (r.bottom - limite) / pxPerMm);
          });
        }
        return {
          pagina: p.dataset.page,
          overflowMm: +pior.toFixed(1),
          alturaConteudoMm: conteudo ? +(conteudo.getBoundingClientRect().height / pxPerMm).toFixed(1) : 0
        };
      });
    };

    window.__RELATORIO_PRONTO__ = true;
  }

  function carregar() {
    if (!window.INTERNET_USERS_DATA) {
      document.body.insertAdjacentHTML("afterbegin",
        '<p style="padding:20px;font-family:sans-serif;color:#8C1246">Base de dados não carregada.</p>');
      return;
    }
    iniciar(window.INTERNET_USERS_DATA);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", carregar);
  else carregar();
})();
