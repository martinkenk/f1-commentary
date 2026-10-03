/* Interactive FastF1 pace-trace charts (speed / delta vs. distance).
 *
 * Each chart is a <figure class="pace-chart"> containing a canvas and a
 * legend, paired with a <script type="application/json" class="pace-chart-data">
 * sibling holding the trace payload written by fastf1_analysis.py:
 *   {distance:[...], unit:"km/h", refCode:null|"VER",
 *    series:[{code,driver,team,color,dash,values}, ...]}
 *
 * Clicking a legend entry toggles that driver's line on/off, and the y-axis
 * rescales to whatever is currently visible so isolating 1-2 traces makes
 * their difference easy to read. The expand button (or clicking the chart)
 * reparents the figure into a fullscreen overlay; closing puts it back.
 */
(function () {
  "use strict";

  function fmtNum(v, decimals) {
    return v.toFixed(decimals);
  }

  function niceAxisValues(min, max, count) {
    if (min === max) { min -= 1; max += 1; }
    var step = (max - min) / (count - 1);
    var out = [];
    for (var i = 0; i < count; i++) out.push(min + step * i);
    return out;
  }

  function PaceChart(figure, payload) {
    this.figure = figure;
    this.canvas = figure.querySelector(".pace-chart-canvas");
    this.ctx = this.canvas.getContext("2d");
    this.legendEl = figure.querySelector(".pace-chart-legend");
    this.data = payload;
    this.visible = {};
    this.valueDecimals = payload.unit === "s" ? 3 : 1;
    var self = this;
    payload.series.forEach(function (s) { self.visible[s.code] = true; });
    this._buildLegend();
    this._bindResize();
    this.draw();
  }

  PaceChart.prototype._bindResize = function () {
    var self = this;
    window.addEventListener("resize", function () { self.draw(); });
  };

  PaceChart.prototype._buildLegend = function () {
    var self = this;
    var frag = document.createDocumentFragment();

    var allBtn = document.createElement("button");
    allBtn.type = "button";
    allBtn.className = "pace-chip pace-chip-all";
    allBtn.textContent = "Show all";
    allBtn.addEventListener("click", function () {
      self.data.series.forEach(function (s) { self.visible[s.code] = true; });
      self._refreshLegendState();
      self.draw();
    });
    frag.appendChild(allBtn);

    this.data.series.forEach(function (s) {
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "pace-chip";
      chip.dataset.code = s.code;
      var swatch = document.createElement("span");
      swatch.className = "pace-chip-swatch" + (s.dash ? " dashed" : "");
      swatch.style.setProperty("--swatch-color", s.color || "#999");
      var label = document.createElement("span");
      label.textContent = s.code + (s.team ? " \u00b7 " + s.team : "");
      chip.title = s.driver || s.code;
      chip.appendChild(swatch);
      chip.appendChild(label);
      chip.addEventListener("click", function () {
        self.visible[s.code] = !self.visible[s.code];
        chip.classList.toggle("off", !self.visible[s.code]);
        self.draw();
      });
      frag.appendChild(chip);
    });
    this.legendEl.innerHTML = "";
    this.legendEl.appendChild(frag);
  };

  PaceChart.prototype._refreshLegendState = function () {
    var self = this;
    this.legendEl.querySelectorAll(".pace-chip[data-code]").forEach(function (chip) {
      chip.classList.toggle("off", !self.visible[chip.dataset.code]);
    });
  };

  PaceChart.prototype.draw = function () {
    var canvas = this.canvas;
    var ctx = this.ctx;
    var rect = canvas.parentElement.getBoundingClientRect();
    var dpr = window.devicePixelRatio || 1;
    var w = Math.max(280, rect.width);
    var h = canvas.parentElement.classList.contains("pace-chart-canvas-wrap-full") ? Math.max(360, rect.height) : Math.round(w * 0.46);
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    var pad = { l: 52, r: 16, t: 14, b: 30 };
    var plotW = w - pad.l - pad.r;
    var plotH = h - pad.t - pad.b;

    var distance = this.data.distance;
    var visibleSeries = this.data.series.filter(function (s) { return this.visible[s.code]; }, this);

    var isDark = getComputedStyle(document.body).getPropertyValue("--panel").trim() !== "";
    var gridColor = "rgba(148,163,184,0.25)";
    var textColor = getComputedStyle(document.body).color || "#ccc";

    ctx.font = "11px system-ui, sans-serif";

    if (!visibleSeries.length) {
      ctx.fillStyle = textColor;
      ctx.globalAlpha = 0.6;
      ctx.fillText("No drivers selected \u2014 click a legend entry to show a trace.", pad.l, h / 2);
      ctx.globalAlpha = 1;
      return;
    }

    var minV = Infinity, maxV = -Infinity;
    visibleSeries.forEach(function (s) {
      s.values.forEach(function (v) {
        if (v < minV) minV = v;
        if (v > maxV) maxV = v;
      });
    });
    if (this.data.refCode !== undefined) {
      // Delta chart: always keep the zero reference line in view.
      minV = Math.min(minV, 0);
      maxV = Math.max(maxV, 0);
    }
    var vPad = (maxV - minV) * 0.08 || 1;
    minV -= vPad;
    maxV += vPad;

    var minD = distance[0], maxD = distance[distance.length - 1];

    function xPix(d) { return pad.l + ((d - minD) / (maxD - minD)) * plotW; }
    function yPix(v) { return pad.t + (1 - (v - minV) / (maxV - minV)) * plotH; }

    // Gridlines + axis labels.
    ctx.strokeStyle = gridColor;
    ctx.fillStyle = textColor;
    ctx.globalAlpha = 0.85;
    var yTicks = niceAxisValues(minV, maxV, 5);
    yTicks.forEach(function (v) {
      var y = yPix(v);
      ctx.beginPath();
      ctx.moveTo(pad.l, y);
      ctx.lineTo(w - pad.r, y);
      ctx.stroke();
      ctx.fillText(fmtNum(v, this.valueDecimals), 4, y + 3);
    }, this);
    var xTicks = niceAxisValues(minD, maxD, 6);
    xTicks.forEach(function (d) {
      var x = xPix(d);
      ctx.fillText(Math.round(d) + "m", x - 14, h - 8);
    });
    ctx.globalAlpha = 1;

    if (this.data.refCode !== undefined) {
      ctx.strokeStyle = "rgba(148,163,184,0.55)";
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.moveTo(pad.l, yPix(0));
      ctx.lineTo(w - pad.r, yPix(0));
      ctx.stroke();
      ctx.setLineDash([]);
    }

    visibleSeries.forEach(function (s) {
      ctx.beginPath();
      ctx.strokeStyle = s.color || "#e10600";
      ctx.lineWidth = 2;
      ctx.setLineDash(s.dash ? [6, 4] : []);
      s.values.forEach(function (v, i) {
        var x = xPix(distance[i]);
        var y = yPix(v);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.setLineDash([]);
    });
  };

  // --------------------------------------------------------------------
  // Fullscreen modal: reparent the clicked figure into an overlay, then
  // restore it on close. Toggle state lives on the PaceChart instance, so
  // it survives the move either direction.
  // --------------------------------------------------------------------
  var modal, modalBody, restoreTarget = null, restoreNext = null, activeChart = null;

  function ensureModal() {
    if (modal) return modal;
    modal = document.createElement("div");
    modal.className = "pace-chart-modal";
    modal.innerHTML = '<button type="button" class="pace-chart-modal-close" aria-label="Close">&times;</button>' +
      '<div class="pace-chart-modal-body"></div>';
    document.body.appendChild(modal);
    modalBody = modal.querySelector(".pace-chart-modal-body");
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeFullscreen();
    });
    modal.querySelector(".pace-chart-modal-close").addEventListener("click", closeFullscreen);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeFullscreen();
    });
    return modal;
  }

  function openFullscreen(figure, chart) {
    ensureModal();
    restoreTarget = figure.parentElement;
    restoreNext = figure.nextSibling;
    figure.classList.add("pace-chart-fullscreen");
    figure.querySelector(".pace-chart-canvas-wrap").classList.add("pace-chart-canvas-wrap-full");
    modalBody.appendChild(figure);
    modal.classList.add("open");
    activeChart = chart;
    requestAnimationFrame(function () { chart.draw(); });
  }

  function closeFullscreen() {
    if (!modal || !modal.classList.contains("open")) return;
    var figure = modalBody.firstElementChild;
    if (figure && restoreTarget) {
      figure.classList.remove("pace-chart-fullscreen");
      figure.querySelector(".pace-chart-canvas-wrap").classList.remove("pace-chart-canvas-wrap-full");
      restoreTarget.insertBefore(figure, restoreNext);
    }
    modal.classList.remove("open");
    if (activeChart) requestAnimationFrame(function () { activeChart.draw(); });
    activeChart = null;
  }

  function init() {
    document.querySelectorAll(".pace-chart-data").forEach(function (scriptEl) {
      var id = scriptEl.dataset.for;
      var figure = document.querySelector('.pace-chart[data-chart-id="' + id + '"]');
      if (!figure) return;
      var payload;
      try {
        payload = JSON.parse(scriptEl.textContent);
      } catch (e) {
        return;
      }
      var chart = new PaceChart(figure, payload);
      figure.__paceChart = chart;
      var expandBtn = figure.querySelector(".pace-chart-expand");
      if (expandBtn) {
        expandBtn.addEventListener("click", function () { openFullscreen(figure, chart); });
      }
    });
  }

  // Charts inside an inactive Bootstrap tab pane have zero width when first
  // drawn (display:none), so redraw once their pane actually becomes
  // visible (fires on the <button data-bs-toggle="pill"> being shown).
  document.addEventListener("shown.bs.tab", function (e) {
    var targetSel = e.target.getAttribute("data-bs-target");
    if (!targetSel) return;
    var pane = document.querySelector(targetSel);
    if (!pane) return;
    pane.querySelectorAll(".pace-chart").forEach(function (figure) {
      if (figure.__paceChart) figure.__paceChart.draw();
    });
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
