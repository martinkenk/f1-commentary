/* Generic sortable + filterable data tables.
 *
 * Applies to every <table class="data"> on the page (results, standings,
 * pace-analysis, tyre-availability, penalties, etc.) without any per-page
 * wiring: clicking a <th> sorts the table by that column (toggling
 * ascending/descending), and a small filter box is injected above tables
 * that opt in via class="data filterable" to do a live text search across
 * every row.
 *
 * Sort comparison: numeric-aware — cells are compared as numbers when the
 * visible text (with the most common decorations stripped: units, "+"
 * gap-prefixes, thousands separators, badge/subtext wrapper text) parses
 * cleanly as a number for every row in that column, otherwise falls back to
 * a locale-aware string comparison. This makes lap times ("1:21.786"),
 * plain numbers, and gap columns ("+0.235s") all sort correctly without any
 * per-table configuration.
 */
(function () {
  "use strict";

  function cellSortValue(td) {
    // Prefer an explicit override (e.g. a badge whose visible text isn't
    // the real sort key) via data-sort, then fall back to visible text.
    var raw = td.getAttribute("data-sort");
    if (raw === null) raw = td.textContent || "";
    return raw.trim();
  }

  function toNumber(text) {
    if (!text) return null;
    var t = text.replace(/,/g, "").trim();
    // "1:21.786" -> 81.786 (mm:ss.sss lap/gap times)
    var m = t.match(/^(\d+):(\d+(?:\.\d+)?)$/);
    if (m) return parseInt(m[1], 10) * 60 + parseFloat(m[2]);
    // Strip a leading "+" (gap columns) and a trailing unit word/symbol.
    var stripped = t.replace(/^\+/, "").replace(/[a-zA-Z%°"'\u2033\u2013\u2014\s]+$/, "");
    if (stripped === "" || isNaN(Number(stripped))) return null;
    return Number(stripped);
  }

  function columnIsNumeric(table, colIndex) {
    var rows = table.tBodies[0] ? table.tBodies[0].rows : [];
    var sawAny = false;
    for (var i = 0; i < rows.length; i++) {
      var td = rows[i].cells[colIndex];
      if (!td) continue;
      var text = cellSortValue(td);
      if (text === "" || text === "\u2014") continue; // blank / em-dash placeholder
      sawAny = true;
      if (toNumber(text) === null) return false;
    }
    return sawAny;
  }

  function sortTable(table, colIndex, numeric, dir) {
    var tbody = table.tBodies[0];
    if (!tbody) return;
    var rows = Array.prototype.slice.call(tbody.rows);
    rows.sort(function (a, b) {
      var ta = a.cells[colIndex] ? cellSortValue(a.cells[colIndex]) : "";
      var tb = b.cells[colIndex] ? cellSortValue(b.cells[colIndex]) : "";
      var cmp;
      if (numeric) {
        var na = toNumber(ta), nb = toNumber(tb);
        if (na === null) na = dir === 1 ? Infinity : -Infinity;
        if (nb === null) nb = dir === 1 ? Infinity : -Infinity;
        cmp = na - nb;
      } else {
        cmp = ta.localeCompare(tb, undefined, { numeric: true, sensitivity: "base" });
      }
      return cmp * dir;
    });
    rows.forEach(function (r) { tbody.appendChild(r); });
  }

  function wireSort(table) {
    if (table.dataset.sortWired) return;
    table.dataset.sortWired = "1";
    var headRow = table.tHead && table.tHead.rows[0];
    if (!headRow) return;
    var state = { col: -1, dir: 1 };
    Array.prototype.forEach.call(headRow.cells, function (th, colIndex) {
      th.classList.add("sortable-th");
      th.setAttribute("role", "button");
      th.setAttribute("tabindex", "0");
      var arrow = document.createElement("span");
      arrow.className = "sort-arrow";
      th.appendChild(arrow);
      function activate() {
        var numeric = columnIsNumeric(table, colIndex);
        state.dir = state.col === colIndex ? -state.dir : 1;
        state.col = colIndex;
        sortTable(table, colIndex, numeric, state.dir);
        Array.prototype.forEach.call(headRow.cells, function (h) {
          h.classList.remove("sort-asc", "sort-desc");
        });
        th.classList.add(state.dir === 1 ? "sort-asc" : "sort-desc");
      }
      th.addEventListener("click", activate);
      th.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); activate(); }
      });
    });
  }

  function wireFilter(table) {
    if (table.dataset.filterWired) return;
    table.dataset.filterWired = "1";
    var wrap = table.closest(".table-wrap") || table.parentElement;
    var box = document.createElement("div");
    box.className = "table-filter";
    box.innerHTML = '<i class="bi bi-search"></i><input type="search" placeholder="Filter rows\u2026" aria-label="Filter table rows">';
    wrap.parentNode.insertBefore(box, wrap);
    var input = box.querySelector("input");
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      var rows = table.tBodies[0] ? table.tBodies[0].rows : [];
      Array.prototype.forEach.call(rows, function (row) {
        var text = row.textContent.toLowerCase();
        row.style.display = q === "" || text.indexOf(q) !== -1 ? "" : "none";
      });
    });
  }

  function init() {
    var tables = document.querySelectorAll("table.data");
    Array.prototype.forEach.call(tables, function (table) {
      if (!table.tHead || !table.tBodies.length) return;
      // Column-head-hierarchy tables (multiple header rows) and single-row
      // reference tables aren't worth wiring — need at least a couple of
      // body rows for sorting/filtering to be useful.
      if (table.tBodies[0].rows.length < 2) return;
      wireSort(table);
      if (table.classList.contains("filterable")) wireFilter(table);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
