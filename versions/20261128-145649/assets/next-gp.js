(() => {
  const events = Array.from(document.querySelectorAll("#gp-options a")).map(link => ({
    link,
    start: Date.parse(link.dataset.start),
    end: Date.parse(link.dataset.end),
  }));
  const status = document.getElementById("redirect-status");
  if (!events.length || events.some(event => !Number.isFinite(event.start) ||
      !Number.isFinite(event.end) || event.end <= event.start)) {
    status.textContent = "The event schedule is unavailable. Choose a Grand Prix below or open the season calendar.";
    return;
  }
  events.sort((a, b) => a.start - b.start);
  const now = Date.now();
  const selected = events.find(event => event.start <= now && now < event.end) ||
    events.find(event => event.start > now);
  if (selected) {
    window.location.replace(selected.link.href);
  } else {
    status.textContent = "The scheduled season is complete. The next season is not yet available here.";
  }
})();
