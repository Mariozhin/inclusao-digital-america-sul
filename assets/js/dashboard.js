/*
 * dashboard.js — camada de apresentação do dashboard.
 *
 * Carrega a base (fetch do JSON canônico com fallback para o espelho JS, permitindo abrir
 * o arquivo via file://), calcula as métricas com Analytics e renderiza cartões, tabelas
 * e os quatro gráficos de linhas com Chart.js.
 */
(function () {
  "use strict";

  var COR = {
    azul: "#1B4F9C",
    azulEscuro: "#0F2C57",
    rosa: "#C2185B",
    verde: "#1E7A45",
    preto: "#111418",
    grade: "#E9EDF2",
    texto: "#24292F",
    fraco: "#5B6672"
  };

  var fmt = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var fmt1 = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  var fmt0 = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });

  function pct(v) { return v === null || v === undefined ? "—" : fmt.format(v) + "%"; }
  function pp(v) {
    if (v === null || v === undefined) return "—";
    return (v > 0 ? "+" : v < 0 ? "−" : "") + fmt.format(Math.abs(v)) + " pp";
  }

  // ---------------------------------------------------------------- carga
  function carregarDados() {
    function usar(dados, origem) {
      dados.__origem = origem;
      iniciar(dados);
    }
    if (window.INTERNET_USERS_DATA) {
      // Espelho carregado por <script> (funciona em file:// e no GitHub Pages)
      usar(window.INTERNET_USERS_DATA, "data/internet_users.js");
      return;
    }
    fetch("data/internet_users.json", { cache: "no-store" })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (d) { usar(d, "data/internet_users.json"); })
      .catch(function (err) { exibirErro(err); });
  }

  function exibirErro(err) {
    var alvo = document.getElementById("aviso-dados");
    if (alvo) {
      alvo.hidden = false;
      alvo.textContent = "Não foi possível carregar a base de dados (" + err.message +
        "). Abra a página por um servidor HTTP local ou verifique data/internet_users.js.";
    }
    console.error(err);
  }

  // ---------------------------------------------------------------- gráficos
  var baseOpts = null;

  function opcoes(tipo) {
    var o = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      animation: { duration: 650 },
      layout: { padding: { top: 8, right: 8, bottom: 0, left: 0 } },
      plugins: {
        legend: {
          position: "bottom",
          align: "center",
          labels: {
            usePointStyle: true,
            pointStyle: "circle",
            boxWidth: 8,
            boxHeight: 8,
            padding: 18,
            color: COR.texto,
            font: { size: 12.5, family: "'Segoe UI', system-ui, sans-serif" }
          }
        },
        tooltip: {
          backgroundColor: "#FFFFFF",
          titleColor: COR.azulEscuro,
          bodyColor: COR.texto,
          borderColor: COR.grade,
          borderWidth: 1,
          padding: 10,
          titleFont: { size: 12.5, weight: "600" },
          bodyFont: { size: 12.5 },
          displayColors: true,
          usePointStyle: true,
          callbacks: {
            title: function (itens) { return "Ano " + itens[0].label; },
            label: function (item) {
              var sufixo = tipo === "pp" ? " pp" : "%";
              return " " + item.dataset.label + ": " + fmt.format(item.parsed.y) + sufixo;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false, drawBorder: false },
          border: { color: COR.grade },
          ticks: {
            color: COR.fraco,
            font: { size: 11.5, family: "'Segoe UI', system-ui, sans-serif" },
            maxRotation: 0,
            autoSkipPadding: 12
          }
        },
        y: {
          beginAtZero: tipo === "pp" ? false : true,
          grid: { color: COR.grade, drawTicks: false, drawBorder: false, lineWidth: 1 },
          border: { display: false },
          ticks: {
            color: COR.fraco,
            padding: 6,
            font: { size: 11.5, family: "'Segoe UI', system-ui, sans-serif" },
            callback: function (v) { return (tipo === "pp" ? v + " pp" : v + "%"); }
          }
        }
      }
    };
    if (tipo !== "pp") {
      o.scales.y.min = 0;
      o.scales.y.max = 100;
      o.scales.y.ticks.stepSize = 20;
    }
    return o;
  }

  function linha(rotulo, valores, cor, extra) {
    var cfg = {
      label: rotulo,
      data: valores,
      borderColor: cor,
      backgroundColor: cor,
      borderWidth: 2.4,
      tension: 0,
      pointRadius: 3.6,
      pointHoverRadius: 6,
      pointBackgroundColor: cor,
      pointBorderColor: "#FFFFFF",
      pointBorderWidth: 1.8,
      pointHitRadius: 12
    };
    if (extra) Object.keys(extra).forEach(function (k) { cfg[k] = extra[k]; });
    return cfg;
  }

  function desenharGraficos(ds, an) {
    var anos = ds.periodo.anos_analise;
    var anosLabel = anos.map(String);

    Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
    Chart.defaults.color = COR.texto;

    var anosCompletos = [];
    for (var a = ds.periodo.serie_completa.inicio; a <= ds.periodo.serie_completa.fim; a++) anosCompletos.push(a);

    // Gráfico 1 — evolução das quatro séries
    new Chart(document.getElementById("grafico-1"), {
      type: "line",
      data: {
        labels: anosLabel,
        datasets: ds.series.map(function (s) {
          return linha(s.nome, an.serie(s.codigo, anos), s.cor);
        })
      },
      options: opcoes("pct")
    });

    // Gráfico 2 — Brasil vs. média dos três países
    var medias = an.mediaEstrangeiros(anos);
    new Chart(document.getElementById("grafico-2"), {
      type: "line",
      data: {
        labels: anosLabel,
        datasets: [
          linha("Brasil", an.serie("BRA", anos), COR.azul),
          linha("Média de Argentina, Chile e Uruguai", medias, COR.rosa,
            { borderDash: [6, 4], borderWidth: 2.2, pointRadius: 3 })
        ]
      },
      options: opcoes("pct")
    });

    // Gráfico 3 — diferença Brasil - país (pontos percentuais)
    new Chart(document.getElementById("grafico-3"), {
      type: "line",
      data: {
        labels: anosLabel,
        datasets: [
          linha("Brasil − Argentina", an.diferencaBrasilPais("ARG", anos), COR.rosa),
          linha("Brasil − Chile", an.diferencaBrasilPais("CHL", anos), COR.verde),
          linha("Brasil − Uruguai", an.diferencaBrasilPais("URY", anos), COR.preto)
        ]
      },
      options: (function () {
        var o = opcoes("pp");
        o.scales.y.min = -25;
        o.scales.y.max = 10;
        o.scales.y.ticks.stepSize = 5;
        return o;
      })()
    });

    // Gráfico 4 (anexo) — série histórica completa, com lacunas preservadas
    new Chart(document.getElementById("grafico-4"), {
      type: "line",
      data: {
        labels: anosCompletos.map(String),
        datasets: ds.series.map(function (s) {
          return linha(s.nome, an.serie(s.codigo, anosCompletos), s.cor,
            { spanGaps: false, pointRadius: 2.4 });
        })
      },
      options: (function () {
        var o = opcoes("pct");
        o.plugins.legend.labels.font.size = 12;
        return o;
      })()
    });
  }

  // ---------------------------------------------------------------- tabelas
  function celula(tr, texto, classe) {
    var td = document.createElement("td");
    td.textContent = texto;
    if (classe) td.className = classe;
    tr.appendChild(td);
    return td;
  }

  function linhaTabela(tbody, rotulo, valores) {
    var tr = document.createElement("tr");
    var th = document.createElement("td");
    th.textContent = rotulo;
    tr.appendChild(th);
    valores.forEach(function (v) { celula(tr, v); });
    tbody.appendChild(tr);
    return tr;
  }

  function renderTabelas(ds, an) {
    var anos = ds.periodo.anos_analise;
    var ultimo = anos[anos.length - 1];

    // Tabela 1 — indicadores por país
    var t1 = document.getElementById("tab-metricas");
    if (t1) {
      ds.series.forEach(function (s) {
        var m = an.metricasPais(s.codigo);
        var tr = linhaTabela(t1, s.nome, [
          pct(m.primeiroValor), pct(m.ultimoValor), pp(m.deltaPP),
          fmt0.format(m.variacaoRelativa) + "%", pct(m.media)
        ]);
        tr.style.setProperty("--cor-serie", s.cor);
        if (s.codigo === "BRA") tr.classList.add("destaque");
      });
      linhaTabela(t1, "Média dos três países", [
        pct(Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, anos[0]); }))),
        pct(Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, ultimo); }))),
        pp(Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, ultimo); })) -
           Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, anos[0]); }))),
        "—",
        pct(Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.metricasPais(c).media; })))
      ]);
    }

    // Tabela 2 — diferenças Brasil x cada país no último ano
    var t2 = document.getElementById("tab-diferencas");
    if (t2) {
      Analytics.ESTRANGEIROS.forEach(function (c) {
        var info = an.info(c);
        var d = an.diferencaBrasilPais(c, anos);
        var menor = Math.min.apply(null, d);
        var maior = Math.max.apply(null, d);
        linhaTabela(t2, "Brasil − " + info.nome, [
          pct(an.valor(c, ultimo)), pp(d[d.length - 1]),
          pp(maior) + " (" + anos[d.indexOf(maior)] + ")",
          pp(menor) + " (" + anos[d.indexOf(menor)] + ")"
        ]);
      });
    }

    // Tabela 3 — subperíodos (pp por ano)
    var t3 = document.getElementById("tab-subperiodos");
    if (t3) {
      an.subperiodos().forEach(function (linhaSub) {
        var tr = linhaTabela(t3, linhaSub.inicio + "–" + linhaSub.fim,
          Analytics.PAISES.map(function (c) { return pp(linhaSub[c].porAno).replace(" pp", "") + " pp/ano"; }));
        tr.firstChild.textContent = linhaSub.inicio + "–" + linhaSub.fim;
      });
    }

    // Cartões de destaque
    var ultimoComp = an.comparativoFinal();
    definir("kpi-brasil-2024", pct(ultimoComp.brasil));
    definir("kpi-brasil-delta", pp(an.metricasPais("BRA").deltaPP));
    definir("kpi-media-2024", pct(ultimoComp.mediaEstrangeiros));
    definir("kpi-diferenca-2024", pp(ultimoComp.diferencaPP));
    definir("kpi-observacoes", fmt0.format(an.auditar().observacoes));
    definir("kpi-ultima-coleta", ds.coleta.data_local);
    definir("kpi-api-atualizada", ds.fonte.api_atualizada_em);
    definir("periodo-analise", ds.periodo.analise.inicio + "–" + ds.periodo.analise.fim);

    // Tabela completa (anexo) — valores por ano
    var tanexo = document.getElementById("tab-completa");
    if (tanexo) {
      anos.forEach(function (ano) {
        var tr = document.createElement("tr");
        celula(tr, String(ano));
        Analytics.PAISES.forEach(function (c) {
          var v = an.valor(c, ano);
          var td = celula(tr, pct(v));
          td.style.color = an.info(c).cor;
          td.style.fontWeight = "600";
        });
        celula(tr, pct(Analytics.media(Analytics.ESTRANGEIROS.map(function (c) { return an.valor(c, ano); }))));
        celula(tr, pp(an.diferencaBrasilMedia(anos)[anos.indexOf(ano)]));
        tanexo.appendChild(tr);
      });
    }
  }

  function definir(id, texto) {
    var el = document.getElementById(id);
    if (el) el.textContent = texto;
  }

  function iniciar(ds) {
    var an = new Analytics(ds);
    var aud = an.auditar();
    var selo = document.getElementById("selo-auditoria");
    if (selo) {
      selo.textContent = aud.ok
        ? "Base validada: " + aud.observacoes + " observações, " + aud.anosAnalise +
          " anos por série, nenhuma lacuna no período de análise."
        : "Atenção: " + aud.problemas.length + " inconsistência(s) detectada(s) na base.";
      selo.className = aud.ok ? "callout" : "aviso-erro";
    }
    renderTabelas(ds, an);
    desenharGraficos(ds, an);
    window.__PRONTO__ = true;
    window.__AUDITORIA__ = aud;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", carregarDados);
  } else {
    carregarDados();
  }
})();
