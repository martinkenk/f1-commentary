/* Generic sortable + filterable data tables.
 *
 * Applies to every <table class="data"> on the page (results, standings,
 * pace-analysis, tyre-availability, penalties, etc.) without any per-page
 * wiring: clicking a <th> sorts the table by that column (toggling
 * ascending/descending). Tables that opt in via class="data filterable"
 * additionally get: (1) a live text-search box, and (2) if every row
 * identifies its driver via a ".drv-code" span in the first cell, a row of
 * clickable driver "chips" — click one or more to show only those drivers
 * (e.g. click VER, NOR and LEC to compare just those three), click a
 * selected chip again to remove it, or "Clear" to reset. The two filters
 * combine (AND) with each other.
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

  // Rows can be hidden for more than one reason at once (text search AND
  // driver-chip selection). Each wired predicate is stored on the table and
  // a row is shown only when every predicate currently accepts it.
  function applyRowFilters(table) {
    var rows = table.tBodies[0] ? table.tBodies[0].rows : [];
    var predicates = table._rowFilterPredicates || [];
    Array.prototype.forEach.call(rows, function (row) {
      var visible = predicates.every(function (p) { return p(row); });
      row.style.display = visible ? "" : "none";
    });
  }

  function addRowFilterPredicate(table, predicate) {
    if (!table._rowFilterPredicates) table._rowFilterPredicates = [];
    table._rowFilterPredicates.push(predicate);
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
    var query = "";
    addRowFilterPredicate(table, function (row) {
      return query === "" || row.textContent.toLowerCase().indexOf(query) !== -1;
    });
    input.addEventListener("input", function () {
      query = input.value.trim().toLowerCase();
      applyRowFilters(table);
    });
  }

  // Per-driver "chip" picker: click one or more driver chips to show only
  // those drivers' rows (click a selected chip again to deselect it; with
  // nothing selected every row shows, same as before). Only wired for
  // tables where every body row identifies its driver via a ".drv-code"
  // span somewhere in the row (results, standings, tyre/pace tables, etc. —
  // the code's column position varies per table, e.g. standings has a
  // leading position-number column, so this isn't assumed to be cell 0).
  function rowDriverCode(row) {
    var span = row.querySelector(".drv-code");
    return span ? span.textContent.trim() : "";
  }

  function driverCodesForTable(table) {
    var rows = table.tBodies[0] ? table.tBodies[0].rows : [];
    var codes = [];
    var seen = {};
    for (var i = 0; i < rows.length; i++) {
      var code = rowDriverCode(rows[i]);
      if (!code) return null; // needs a code on every row to be reliable
      if (seen[code]) continue;
      seen[code] = true;
      codes.push(code);
    }
    return codes.length > 1 ? codes : null;
  }

  function wireDriverFilter(table) {
    if (table.dataset.driverFilterWired) return;
    var codes = driverCodesForTable(table);
    if (!codes) return;
    table.dataset.driverFilterWired = "1";
    var wrap = table.closest(".table-wrap") || table.parentElement;
    var bar = document.createElement("div");
    bar.className = "driver-chip-bar";
    var label = document.createElement("span");
    label.className = "driver-chip-label";
    label.textContent = "Drivers:";
    bar.appendChild(label);
    var selected = {};
    var chips = {};
    function refresh() {
      Object.keys(chips).forEach(function (code) {
        chips[code].classList.toggle("active", !!selected[code]);
      });
    }
    codes.forEach(function (code) {
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "driver-chip";
      chip.textContent = code;
      chip.addEventListener("click", function () {
        if (selected[code]) delete selected[code];
        else selected[code] = true;
        refresh();
        applyRowFilters(table);
      });
      chips[code] = chip;
      bar.appendChild(chip);
    });
    var clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "driver-chip driver-chip-clear";
    clearBtn.textContent = "Clear";
    clearBtn.addEventListener("click", function () {
      selected = {};
      refresh();
      applyRowFilters(table);
    });
    bar.appendChild(clearBtn);
    wrap.parentNode.insertBefore(bar, wrap);
    addRowFilterPredicate(table, function (row) {
      if (Object.keys(selected).length === 0) return true;
      return !!selected[rowDriverCode(row)];
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
      if (table.classList.contains("filterable")) {
        wireDriverFilter(table);
        wireFilter(table);
        applyRowFilters(table);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
