/*
 * svg-chart.js — renderizador de gráficos de linhas em SVG, otimizado para impressão.
 *
 * Gera gráficos vetoriais (nítidos em qualquer resolução de PDF), com:
 *   - fundo branco, grade horizontal discreta e sem grade vertical;
 *   - marcadores circulares com contorno branco;
 *   - legenda centralizada abaixo da área de plotagem;
 *   - eixos com percentuais/valores explícitos;
 *   - descontinuidade visual nos anos sem observação (spanGaps desativado).
 *
 * API:
 *   SVGChart.linhas(container, {
 *     largura, altura, anos, series: [{nome, cor, valores, tracejado}],
 *     yMin, yMax, yPasso, sufixo, casas, zero
 *   })
 */
(function (global) {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";

  function el(nome, attrs, texto) {
    var n = document.createElementNS(NS, nome);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (texto !== undefined && texto !== null) n.textContent = texto;
    return n;
  }

  function fmt(v, casas) {
    return new Intl.NumberFormat("pt-BR", {
      minimumFractionDigits: casas === undefined ? 0 : casas,
      maximumFractionDigits: casas === undefined ? 0 : casas
    }).format(v);
  }

  function linhas(container, cfg) {
    var W = cfg.largura || 900;
    var H = cfg.altura || 430;
    var sufixo = cfg.sufixo || "";
    var casas = cfg.casas === undefined ? 0 : cfg.casas;
    var anos = cfg.anos;

    var margem = { topo: 18, direita: 22, base: 74, esquerda: 62 };
    var x0 = margem.esquerda, x1 = W - margem.direita;
    var y0 = margem.topo, y1 = H - margem.base;

    var yMin = cfg.yMin, yMax = cfg.yMax;
    var escalaY = function (v) { return y1 - ((v - yMin) / (yMax - yMin)) * (y1 - y0); };
    var escalaX = function (i) {
      return anos.length === 1 ? (x0 + x1) / 2 : x0 + (i * (x1 - x0)) / (anos.length - 1);
    };

    container.innerHTML = "";
    var svg = el("svg", {
      viewBox: "0 0 " + W + " " + H,
      width: "100%",
      role: "img",
      "aria-label": cfg.rotulo || "Gráfico de linhas",
      preserveAspectRatio: "xMidYMid meet"
    });
    svg.style.width = "100%";
    svg.style.height = "auto";
    svg.style.aspectRatio = W + " / " + H;
    svg.appendChild(el("title", null, cfg.rotulo || "Gráfico de linhas"));

    // fundo
    svg.appendChild(el("rect", { x: 0, y: 0, width: W, height: H, fill: "#FFFFFF" }));

    // grade horizontal
    var passo = cfg.yPasso || ((yMax - yMin) / 5);
    for (var v = yMin; v <= yMax + 1e-9; v += passo) {
      var yy = escalaY(v);
      svg.appendChild(el("line", {
        x1: x0, x2: x1, y1: yy.toFixed(2), y2: yy.toFixed(2),
        stroke: "#E9EDF2", "stroke-width": 1
      }));
      svg.appendChild(el("text", {
        x: x0 - 10, y: (yy + 5).toFixed(2), "text-anchor": "end",
        "font-family": "'Segoe UI', system-ui, sans-serif", "font-size": 15, fill: "#5B6672"
      }, fmt(v, casas) + sufixo));
    }

    // linha de zero (gráficos de diferença)
    if (cfg.zero && yMin < 0 && yMax > 0) {
      svg.appendChild(el("line", {
        x1: x0, x2: x1, y1: escalaY(0), y2: escalaY(0), stroke: "#AEB8C6", "stroke-width": 1.2
      }));
    }

    // eixo X
    svg.appendChild(el("line", {
      x1: x0, x2: x1, y1: y1, y2: y1, stroke: "#CBD4E0", "stroke-width": 1
    }));

    // rótulos do eixo X
    var pulo = cfg.puloAnos || 1;
    anos.forEach(function (ano, i) {
      if (i % pulo !== 0 && i !== anos.length - 1) return;
      svg.appendChild(el("text", {
        x: escalaX(i).toFixed(2), y: y1 + 24, "text-anchor": "middle",
        "font-family": "'Segoe UI', system-ui, sans-serif", "font-size": 15, fill: "#5B6672"
      }, String(ano)));
    });

    // séries
    cfg.series.forEach(function (s) {
      var segmento = [];
      var segmentos = [];
      s.valores.forEach(function (val, i) {
        if (val === null || val === undefined || isNaN(val)) {
          if (segmento.length) { segmentos.push(segmento); segmento = []; }
        } else {
          segmento.push([escalaX(i), escalaY(val)]);
        }
      });
      if (segmento.length) segmentos.push(segmento);

      segmentos.forEach(function (seg) {
        if (seg.length < 2) return;
        var d = seg.map(function (p, k) {
          return (k === 0 ? "M" : "L") + p[0].toFixed(2) + " " + p[1].toFixed(2);
        }).join(" ");
        var linha = el("path", {
          d: d, fill: "none", stroke: s.cor, "stroke-width": 2.6,
          "stroke-linejoin": "round", "stroke-linecap": "round"
        });
        if (s.tracejado) linha.setAttribute("stroke-dasharray", "7 5");
        svg.appendChild(linha);
      });

      // marcadores
      s.valores.forEach(function (val, i) {
        if (val === null || val === undefined || isNaN(val)) return;
        svg.appendChild(el("circle", {
          cx: escalaX(i).toFixed(2), cy: escalaY(val).toFixed(2), r: 4.4,
          fill: s.cor, stroke: "#FFFFFF", "stroke-width": 1.9
        }));
      });
    });

    // legenda centralizada abaixo do gráfico
    var legenda = el("g", {});
    svg.appendChild(legenda);
    var itens = [];

    // o SVG precisa estar no documento antes da medição dos textos (getBBox)
    container.appendChild(svg);

    cfg.series.forEach(function (s) {
      var g = el("g", {});
      var amostraX = 4, meioY = 0;
      if (s.tracejado) {
        g.appendChild(el("line", {
          x1: 0, x2: 26, y1: meioY, y2: meioY, stroke: s.cor,
          "stroke-width": 2.4, "stroke-dasharray": "7 5"
        }));
      }
      g.appendChild(el("circle", {
        cx: 13, cy: meioY, r: 4.4, fill: s.cor, stroke: "#FFFFFF", "stroke-width": 1.9
      }));
      var t = el("text", {
        x: 24, y: 5, "font-family": "'Segoe UI', system-ui, sans-serif",
        "font-size": 15.5, fill: "#24292F"
      }, s.nome);
      g.appendChild(t);
      legenda.appendChild(g);
      itens.push(g);
    });

    // medição em duas passadas
    var larguras = itens.map(function (g) { return g.getBBox().width; });
    var espaco = 34;
    var total = larguras.reduce(function (a, b) { return a + b; }, 0) + espaco * (itens.length - 1);
    var cursor = Math.max(x0, (W - total) / 2);
    itens.forEach(function (g, i) {
      g.setAttribute("transform", "translate(" + cursor.toFixed(2) + "," + (H - 26) + ")");
      cursor += larguras[i] + espaco;
    });

    return svg;
  }

  global.SVGChart = { linhas: linhas, formatar: fmt };
})(window);
