/* Read already-rendered FIA figures without relying on a browser PDF viewer. */
(function () {
  "use strict";
  var links = document.querySelectorAll("[data-document-reader]");
  if (!links.length) return;

  var dialog = document.createElement("dialog");
  dialog.className = "document-reader";
  dialog.setAttribute("aria-labelledby", "document-reader-title");
  dialog.innerHTML =
    '<header><h2 id="document-reader-title"></h2>' +
    '<button type="button" data-close autofocus>Close</button></header>' +
    '<nav aria-label="Document pages">' +
    '<button type="button" data-previous>Previous</button>' +
    '<span data-page aria-live="polite"></span>' +
    '<button type="button" data-next>Next</button>' +
    '<button type="button" data-zoom aria-pressed="false">Zoom in</button>' +
    '<a data-source target="_blank" rel="noopener">Original FIA PDF</a></nav>' +
    '<p class="document-reader-status" role="status"></p>' +
    '<div class="document-reader-viewport" tabindex="0" aria-label="Scrollable document page"></div>' +
    '<p class="document-reader-caption"></p>';
  document.body.appendChild(dialog);

  var viewport = dialog.querySelector(".document-reader-viewport");
  var status = dialog.querySelector("[role=status]");
  var previous = dialog.querySelector("[data-previous]");
  var next = dialog.querySelector("[data-next]");
  var zoom = dialog.querySelector("[data-zoom]");
  var figures = [], index = 0, opener;

  function showPage() {
    var figure = figures[index];
    var original = figure.querySelector("img");
    var source = figure.querySelector("figcaption a");
    var image = document.createElement("img");
    image.alt = original.alt;
    image.onload = function () {
      if (viewport.firstElementChild === image) {
        image.style.setProperty("--document-native-width", image.naturalWidth + "px");
        status.textContent = "";
      }
    };
    image.onerror = function () {
      if (viewport.firstElementChild === image) {
        status.textContent = "This page image could not load. Use the original FIA PDF link.";
      }
    };
    status.textContent = "Loading page...";
    viewport.classList.remove("zoomed");
    viewport.replaceChildren(image);
    viewport.scrollTo(0, 0);
    zoom.setAttribute("aria-pressed", "false");
    zoom.textContent = "Zoom in";
    previous.disabled = index === 0;
    next.disabled = index === figures.length - 1;
    dialog.querySelector("[data-page]").textContent = (index + 1) + " / " + figures.length;
    dialog.querySelector("[data-source]").href = source.href;
    dialog.querySelector(".document-reader-caption").textContent = original.alt;
    image.src = original.src;
  }

  links.forEach(function (link) {
    link.addEventListener("click", function (event) {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      var target = document.getElementById(link.hash.slice(1));
      if (!target) return; // Preserve native anchor navigation if the target is unavailable.
      if (typeof dialog.showModal !== "function") {
        target.open = true;
        return;
      }
      figures = Array.from(target.querySelectorAll("figure")).filter(function (figure) {
        return figure.querySelector("img") && figure.querySelector("figcaption a");
      });
      if (!figures.length) {
        target.open = true;
        return;
      }
      event.preventDefault();
      opener = link;
      index = 0;
      dialog.querySelector("h2").textContent = link.dataset.readerTitle;
      showPage();
      dialog.showModal();
      document.documentElement.classList.add("document-reader-open");
    });
  });
  previous.addEventListener("click", function () {
    if (index > 0) { index--; showPage(); }
  });
  next.addEventListener("click", function () {
    if (index < figures.length - 1) { index++; showPage(); }
  });
  zoom.addEventListener("click", function () {
    var expanded = viewport.classList.toggle("zoomed");
    zoom.setAttribute("aria-pressed", String(expanded));
    zoom.textContent = expanded ? "Fit width" : "Zoom in";
  });
  dialog.querySelector("[data-close]").addEventListener("click", function () {
    dialog.close();
  });
  dialog.addEventListener("close", function () {
    document.documentElement.classList.remove("document-reader-open");
    if (opener) opener.focus();
  });
})();
