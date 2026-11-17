/*
 * analytics.js — Cálculos reprodutíveis do projeto "Inclusão Digital na América do Sul".
 *
 * Todas as métricas apresentadas no dashboard e no relatório são derivadas exclusivamente da
 * base coletada em data/internet_users.json. Nenhum valor é digitado manualmente.
 *
 * Convenções:
 *  - "pp"  = ponto percentual  -> diferença aritmética entre dois percentuais.
 *  - "variação relativa (%)"   -> (final - inicial) / inicial * 100.
 *  - Células sem observação permanecem null; nunca são tratadas como zero.
 */
(function (global) {
  "use strict";

  var PAISES = ["BRA", "ARG", "CHL", "URY"];
  var ESTRANGEIROS = ["ARG", "CHL", "URY"];

  function arred(x, casas) {
    if (x === null || x === undefined || isNaN(x)) return null;
    var f = Math.pow(10, casas === undefined ? 2 : casas);
    return Math.round((x + Number.EPSILON) * f) / f;
  }

  function media(arr) {
    var v = arr.filter(function (x) { return x !== null && x !== undefined && !isNaN(x); });
    if (!v.length) return null;
    return v.reduce(function (a, b) { return a + b; }, 0) / v.length;
  }

  function indexar(serie) {
    var map = {};
    serie.dados.forEach(function (d) { map[d.ano] = d.valor; });
    return map;
  }

  function Analytics(dataset) {
    this.ds = dataset;
    this.anos = dataset.periodo.anos_analise.slice();
    this.indice = {};
    var self = this;
    dataset.series.forEach(function (s) { self.indice[s.codigo] = indexar(s); });
  }

  Analytics.prototype.info = function (codigo) {
    return this.ds.series.filter(function (s) { return s.codigo === codigo; })[0];
  };

  /** Valor observado de um país em um ano (null se ausente). */
  Analytics.prototype.valor = function (codigo, ano) {
    var m = this.indice[codigo];
    if (!m || !(ano in m)) return null;
    return m[ano];
  };

  /** Série alinhada ao eixo de anos informado; anos sem observação ficam null. */
  Analytics.prototype.serie = function (codigo, anos) {
    var self = this;
    return (anos || this.anos).map(function (a) { return self.valor(codigo, a); });
  };

  /** Média aritmética anual de Argentina, Chile e Uruguai. */
  Analytics.prototype.mediaEstrangeiros = function (anos) {
    var self = this;
    return (anos || this.anos).map(function (a) {
      return media(ESTRANGEIROS.map(function (c) { return self.valor(c, a); }));
    });
  };

  /** Diferença anual Brasil - média(ARG, CHL, URY), em pontos percentuais. */
  Analytics.prototype.diferencaBrasilMedia = function (anos) {
    var self = this;
    return (anos || this.anos).map(function (a, i) {
      var b = self.valor("BRA", a);
      var m = self.mediaEstrangeiros()[i];
      return (b === null || m === null) ? null : b - m;
    });
  };

  /** Diferença anual Brasil - país, em pontos percentuais. */
  Analytics.prototype.diferencaBrasilPais = function (codigo, anos) {
    var self = this;
    return (anos || this.anos).map(function (a) {
      var b = self.valor("BRA", a);
      var p = self.valor(codigo, a);
      return (b === null || p === null) ? null : b - p;
    });
  };

  /** Métricas descritivas de um país no período de análise. */
  Analytics.prototype.metricasPais = function (codigo) {
    var self = this;
    var anos = this.anos;
    var vals = this.serie(codigo);
    var observados = vals.filter(function (v) { return v !== null; });
    var primeiroAno = anos[vals.findIndex(function (v) { return v !== null; })];
    var ultimoIdx = vals.length - 1 - vals.slice().reverse().findIndex(function (v) { return v !== null; });
    var ultimoAno = anos[ultimoIdx];
    var primeiro = vals[anos.indexOf(primeiroAno)];
    var ultimo = vals[ultimoIdx];

    var variacoes = [];
    for (var i = 1; i < anos.length; i++) {
      if (vals[i] !== null && vals[i - 1] !== null) {
        variacoes.push({ ano: anos[i], delta: vals[i] - vals[i - 1] });
      }
    }
    var maiorAlta = variacoes.slice().sort(function (a, b) { return b.delta - a.delta; })[0] || null;
    var maiorQueda = variacoes.slice().sort(function (a, b) { return a.delta - b.delta; })[0] || null;
    var quedas = variacoes.filter(function (v) { return v.delta < 0; });

    return {
      codigo: codigo,
      nome: this.info(codigo).nome,
      cor: this.info(codigo).cor,
      primeiroAno: primeiroAno,
      ultimoAno: ultimoAno,
      primeiroValor: primeiro,
      ultimoValor: ultimo,
      deltaPP: (primeiro !== null && ultimo !== null) ? ultimo - primeiro : null,
      variacaoRelativa: (primeiro && primeiro !== 0) ? ((ultimo - primeiro) / primeiro) * 100 : null,
      media: media(observados),
      minimo: observados.length ? Math.min.apply(null, observados) : null,
      maximo: observados.length ? Math.max.apply(null, observados) : null,
      variacoes: variacoes,
      maiorAlta: maiorAlta,
      maiorQueda: maiorQueda,
      anosDeQueda: quedas.map(function (q) { return q.ano; }),
      nObservacoes: observados.length,
      serie: vals
    };
  };

  /** Análise por subperíodo (variação total em pp e média anual em pp/ano). */
  Analytics.prototype.subperiodos = function (faixas) {
    var self = this;
    var out = [];
    (faixas || [[2000, 2009], [2010, 2019], [2020, 2024]]).forEach(function (f) {
      var linha = { inicio: f[0], fim: f[1], anos: f[1] - f[0] };
      PAISES.forEach(function (c) {
        var a = self.valor(c, f[0]), b = self.valor(c, f[1]);
        linha[c] = (a === null || b === null) ? null : {
          deltaPP: b - a,
          porAno: (b - a) / (f[1] - f[0]),
          inicio: a,
          fim: b
        };
      });
      out.push(linha);
    });
    return out;
  };

  /** País líder (maior percentual) em cada ano, e contagem de liderança. */
  Analytics.prototype.lideranca = function () {
    var self = this;
    var porAno = [];
    var contagem = {};
    PAISES.forEach(function (c) { contagem[c] = 0; });
    this.anos.forEach(function (a) {
      var melhor = null;
      PAISES.forEach(function (c) {
        var v = self.valor(c, a);
        if (v !== null && (melhor === null || v > melhor.valor)) melhor = { codigo: c, valor: v };
      });
      if (melhor) { contagem[melhor.codigo]++; melhor.ano = a; porAno.push(melhor); }
    });
    return { porAno: porAno, contagem: contagem };
  };

  /** Amplitude (maior - menor) entre os quatro países em cada ano, em pp. */
  Analytics.prototype.amplitude = function () {
    var self = this;
    return this.anos.map(function (a) {
      var vals = PAISES.map(function (c) { return self.valor(c, a); }).filter(function (v) { return v !== null; });
      return vals.length > 1 ? Math.max.apply(null, vals) - Math.min.apply(null, vals) : null;
    });
  };

  /** Cálculo da média Brasil vs estrangeiros no último ano do período. */
  Analytics.prototype.comparativoFinal = function () {
    var self = this;
    var ano = this.anos[this.anos.length - 1];
    var b = this.valor("BRA", ano);
    var med = media(ESTRANGEIROS.map(function (c) { return self.valor(c, ano); }));
    return { ano: ano, brasil: b, mediaEstrangeiros: med, diferencaPP: b - med };
  };

  /** Auditoria: confere integridade da base (duplicidades, lacunas, ordem). */
  Analytics.prototype.auditar = function () {
    var self = this;
    var problemas = [];
    this.ds.series.forEach(function (s) {
      var vistos = {};
      s.dados.forEach(function (d) {
        if (vistos[d.ano]) problemas.push("Ano duplicado em " + s.codigo + ": " + d.ano);
        vistos[d.ano] = true;
        if (d.valor === null || d.valor === undefined) problemas.push("Valor nulo em " + s.codigo + " " + d.ano);
        if (typeof d.valor === "number" && (d.valor < 0 || d.valor > 100)) {
          problemas.push("Valor fora de 0-100 em " + s.codigo + " " + d.ano + ": " + d.valor);
        }
      });
      var ordem = s.dados.map(function (d) { return d.ano; });
      for (var i = 1; i < ordem.length; i++) {
        if (ordem[i] <= ordem[i - 1]) problemas.push("Série fora de ordem em " + s.codigo + ": " + ordem[i]);
      }
    });
    this.anos.forEach(function (a) {
      PAISES.forEach(function (c) {
        if (self.valor(c, a) === null) problemas.push("Lacuna no período de análise: " + c + " " + a);
      });
    });
    return {
      ok: problemas.length === 0,
      problemas: problemas,
      anosAnalise: this.anos.length,
      paises: PAISES.length,
      observacoes: this.ds.series.reduce(function (acc, s) { return acc + s.dados.length; }, 0)
    };
  };

  Analytics.arred = arred;
  Analytics.media = media;
  Analytics.PAISES = PAISES;
  Analytics.ESTRANGEIROS = ESTRANGEIROS;

  if (typeof module !== "undefined" && module.exports) module.exports = Analytics;
  global.Analytics = Analytics;
})(typeof window !== "undefined" ? window : global);
