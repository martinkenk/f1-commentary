(function () {
  "use strict";
  document.querySelectorAll("[data-briefing-expires]").forEach(function (section) {
    var expires = Date.parse(section.dataset.briefingExpires);
    var reviewed = section.querySelector("[data-briefing-reviewed]");
    var fallback = section.querySelector("[data-briefing-fallback]");
    if (!Number.isFinite(expires) || !reviewed || !fallback) return;
    function update() {
      var remaining = expires - Date.now();
      if (remaining <= 0) {
        reviewed.hidden = true;
        fallback.hidden = false;
      } else {
        setTimeout(update, Math.min(remaining, 2147483647));
      }
    }
    update();
  });
})();
