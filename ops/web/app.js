"use strict";
const $ = id => document.getElementById(id);
let csrf = "", snapshot = null, selectedRun = null, refreshing = false, setup = false;
const terminal = `${location.protocol}//${location.hostname}:7681/`;
$("terminal-login").href = terminal;
$("terminal-workspace").href = terminal;
const tone = status => ["healthy", "fixed", "active", "completed"].includes(status) ? "good" :
  ["running", "queued", "read_only", "waiting", "waiting_publication"].includes(status) ? "warn" : "bad";
const pretty = value => JSON.stringify(value, null, 2);
const stamp = value => value ? new Date(value).toLocaleString(undefined, {hour12: false}) : "Not recorded";
function node(tag, text, cls) {
  const element = document.createElement(tag);
  if (text !== undefined && text !== null) element.textContent = text;
  if (cls) element.className = cls;
  return element;
}
function badge(text) { return node("span", text || "unknown", `tag ${tone(text)}`); }
function recoveryPanel(recovery, run) {
  const box = node("div", null, "recovery-panel");
  box.append(node("strong", recovery.automatic ? "AUTOMATIC RECOVERY" : "ACTION REQUIRED"),
    node("p", recovery.cause), node("p", recovery.next_step));
  if (recovery.action === "terminal") {
    const link = node("a", `${recovery.label} ↗`);
    link.href = terminal; link.target = "_blank"; link.rel = "noopener"; box.append(link);
  } else if (recovery.action === "recover") {
    const button = node("button", recovery.label, "primary");
    button.onclick = async () => {
      if (!confirm(recovery.confirmation)) return;
      button.disabled = true;
      try { await act("recover", {run_id: run, confirmed: true}); } finally { button.disabled = false; }
    };
    box.append(button);
  }
  return box;
}
function notify(message, error = false) {
  $("notice").textContent = message;
  $("notice").className = error ? "error" : "";
  $("notice").hidden = false;
}
async function api(path, body) {
  const options = {headers: {}};
  if (body !== undefined) {
    options.method = "POST";
    options.headers = {"Content-Type": "application/json", "X-CSRF-Token": csrf};
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  const data = await response.json();
  if (response.status === 401) {
    $("workspace").hidden = true;
    $("login").hidden = false;
  }
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
function tab(name) {
  document.querySelectorAll(".tab").forEach(panel => panel.hidden = panel.id !== name);
  document.querySelectorAll("[data-tab]").forEach(button => button.classList.toggle("active", button.dataset.tab === name));
  $("tab-label").textContent = name.toUpperCase();
  if (name === "repository") loadRepository().catch(error => notify(error.message, true));
}
function metric(label, value, detail, cls) {
  const card = node("article", null, "metric");
  card.append(node("div", label, "eyebrow"), node("div", value, `value ${cls || ""}`), node("small", detail));
  return card;
}
function render(data) {
  snapshot = data;
  const clock = data.scheduler || {}, latest = data.latest || {};
  const timer = data.units["f1-calendar.timer"] || {}, worker = data.units["f1-watchdog.service"] || {};
  const active = ["active", "activating"].includes(worker.ActiveState);
  const queued = data.tasks.filter(job => job.status === "queued").length;
  const last = data.runs.find(run => run.finished_at);
  $("metrics").replaceChildren(
    metric("CALENDAR MONITOR", timer.ActiveState === "active" ? (data.scheduler_stale ? "Stale" : "Monitoring") : "Paused / unavailable",
      `Last tick ${stamp(clock.checked_at)}`, timer.ActiveState === "active" && !data.scheduler_stale ? "good" : "bad"),
    metric("REPAIR WORKER", active ? "Agent running" : "Standby", active ? `Started ${stamp(latest.started_at)}` : `Last run ${stamp(last?.finished_at)}`,
      active ? "warn" : ""),
    metric("COVERAGE ATTENTION", String((clock.coverage_findings || []).length),
      `${(clock.pending || []).length} pending deadlines / ${(clock.errors || []).length} clock errors`,
      (clock.errors || []).length ? "warn" : "good"),
    metric("AGENT QUEUE", String(queued), `${data.preferences?.audit_only ? "Read-only" : "Publish when safe"} / serialized writers`, queued ? "warn" : "")
  );
  const blockers = [...data.errors, ...(clock.errors || [])];
  if (data.scheduler_stale) blockers.unshift("The calendar heartbeat is missing or over three minutes old. Automation may not be monitoring.");
  if (timer.ActiveState !== "active") blockers.unshift("Calendar scheduling is paused or unavailable. New collection will not be scheduled.");
  if (data.preferences?.agent_blocked_reason) blockers.push(`Agent blocker: ${data.preferences.agent_blocked_reason}`);
  $("blockers").textContent = blockers.join("\n");
  $("blockers").hidden = !blockers.length;
  $("deadlines").replaceChildren();
  const deadlines = [...(clock.pending || []), ...(clock.next || [])].slice(0, 8);
  if (!deadlines.length) $("deadlines").append(node("p", "No upcoming deadlines recorded.", "muted"));
  deadlines.forEach(deadline => {
    const row = node("div", null, "deadline"), label = node("div");
    label.append(node("strong", `${deadline.gp || "Coverage"} / ${deadline.session || deadline.kind || "Job"}`),
      node("small", `${deadline.kind || "collection"}${deadline.status ? ` / ${deadline.status}` : ""}`));
    const dates = node("time");
    dates.append(node("div", `Collect ${stamp(deadline.due || deadline.next_poll)}`),
      node("div", `Deadline ${stamp(deadline.deadline)}`));
    row.append(label, dates); $("deadlines").append(row);
  });
  $("latest-status").replaceWith(Object.assign(badge(latest.status), {id: "latest-status"}));
  $("latest-summary").textContent = latest.summary || latest.error || latest.publication_deferred || "No completed report yet.";
  $("latest-meta").replaceChildren();
  [["Started", stamp(latest.started_at)], ["Finished", stamp(latest.finished_at)], ["Policy", latest.mode],
    ["Conversation", latest.session_id]].forEach(([key, value]) => {
    $("latest-meta").append(node("dt", key), node("dd", value || "Not recorded"));
  });
  $("findings").replaceChildren();
  (clock.coverage_findings || []).forEach(finding => {
    const row = node("div", null, "finding");
    row.append(node("span", finding.gp || finding.kind, "tag warn"),
      node("p", finding.message || pretty(finding))); $("findings").append(row);
  });
  if (!(clock.coverage_findings || []).length) $("findings").append(node("p", "No recorded findings. Check heartbeat freshness before treating this as healthy.", "muted"));
  $("tasks").replaceChildren();
  $("queue-count").textContent = `${queued} WAITING`;
  [...data.tasks].reverse().slice(0, 30).forEach(job => {
    const card = node("div", null, "job"), head = node("div", null, "card-head");
    head.append(node("strong", job.title), badge(job.status)); card.append(head);
    card.append(node("p", job.summary || job.error || job.prompt.slice(0, 220)),
      node("small", `${stamp(job.created_at)} / ${job.mode}`));
    const buttons = node("div", null, "button-row");
    if (job.run_id) {
      const inspect = node("button", "Inspect run", "quiet");
      inspect.onclick = () => openRun(job.run_id).catch(error => notify(error.message, true)); buttons.append(inspect);
    }
    if (job.status === "queued") {
      const cancel = node("button", "Cancel", "quiet");
      cancel.onclick = () => act("cancel", {id: job.id}); buttons.append(cancel);
    }
    if (["blocked", "failed", "agent_failed", "timed_out", "interrupted", "read_only"].includes(job.status)) {
      const retry = node("button", "Use prompt again", "quiet");
      retry.onclick = () => { $("task-title").value = job.title; $("task-prompt").value = job.prompt;
        $("task-mode").value = job.mode; tab("agents"); }; buttons.append(retry);
    }
    card.append(buttons); $("tasks").append(card);
  });
  if (!data.tasks.length) $("tasks").append(node("p", "No operator jobs yet. Automatic coverage repairs run independently.", "muted"));
  $("history-rows").replaceChildren();
  data.runs.forEach(run => {
    const row = node("tr"), first = node("td"), inspect = node("button", run.run_id);
    inspect.onclick = () => openRun(run.run_id).catch(error => notify(error.message, true));
    first.append(inspect); const state = node("td"); state.append(badge(run.status));
    const summary = node("td", run.summary || "No final summary yet");
    if (run.recovery && run.status !== "running") summary.append(recoveryPanel(run.recovery, run.run_id));
    row.append(first, node("td", run.task_title || "Coverage audit"), state, node("td", run.mode),
      summary); $("history-rows").append(row);
  });
  const chosen = $("task-resume").value;
  $("task-resume").replaceChildren(new Option("New agent session", ""));
  data.runs.forEach(run => $("task-resume").add(new Option(`${run.run_id} / ${run.task_title || run.status}`, run.run_id)));
  $("task-resume").value = chosen;
  if (!$("guidance").dataset.loaded) {
    $("guidance").value = data.guidance; $("guidance").dataset.loaded = "true";
  }
  $("policy-label").textContent = data.preferences?.audit_only ? "READ ONLY / reports, no publication" : "PUBLISH / verified changes when safe";
  $("operator-events").textContent = data.events;
}
async function refresh() {
  if (refreshing || $("workspace").hidden) return;
  refreshing = true;
  try {
    const data = await api("/api/status"); render(data);
    $("connection").textContent = `Live / ${new Date().toLocaleTimeString()}`; $("connection").className = "good";
    if (selectedRun) await loadRun();
  } catch (error) {
    $("connection").textContent = "Disconnected / displayed data may be stale"; $("connection").className = "bad";
    notify(error.message, true);
  } finally { refreshing = false; }
}
async function loadRun() {
  const run = selectedRun;
  const [report, log] = await Promise.all([api(`/api/runs/${run}/report`), api(`/api/runs/${run}/log`)]);
  if (run !== selectedRun) return;
  $("report").textContent = pretty(report.report);
  $("run-recovery").replaceChildren();
  $("run-recovery").hidden = !report.recovery;
  if (report.recovery) $("run-recovery").append(recoveryPanel(report.recovery, run));
  $("run-publication").hidden = !report.publication?.verified_at;
  $("run-publication").textContent = report.publication?.verified_at ?
    `Publication independently verified ${stamp(report.publication.verified_at)} / deployment ${report.publication.run_id}. Original audit below is preserved unchanged.` : "";
  if (report.resolution?.resolved_at) {
    $("run-publication").hidden = false;
    $("run-publication").textContent = `Resolved ${stamp(report.resolution.resolved_at)} by ${report.resolution.resolved_by}: ${report.resolution.basis}. Original report below is retained as historical evidence.`;
  }
  const box = $("agent-log"), atEnd = box.scrollTop + box.clientHeight >= box.scrollHeight - 40;
  box.textContent = log.text;
  if (atEnd) box.scrollTop = box.scrollHeight;
}
async function openRun(run) {
  selectedRun = run; $("run-title").textContent = run; $("run-detail").hidden = false;
  await loadRun(); $("run-detail").scrollIntoView({behavior: "smooth", block: "start"});
}
async function act(action, data = {}) {
  try {
    const result = await api(`/api/actions/${action}`, data);
    notify(result.message || `Job queued: ${result.task?.title || result.task?.status}`);
    await refresh(); return result;
  } catch (error) { notify(error.message, true); return null; }
}
async function loadRepository() {
  const data = await api("/api/repository");
  $("repo-status").textContent = data.status + "\n\n" + data.commits;
  $("repo-diff").textContent = data.diff || "No uncommitted tracked changes.";
}
document.querySelectorAll("[data-tab]").forEach(button => button.onclick = () => tab(button.dataset.tab));
document.querySelectorAll("[data-action]").forEach(button => button.onclick = async () => {
  const action = button.dataset.action;
  if (["stop", "pause"].includes(action) && !confirm(action === "stop" ?
    "Stop the current agent? Unfinished edits remain. Automatic scheduling and queued tasks are unchanged." :
    "Pause automatic calendar monitoring? It stays paused until resumed. Explicitly queued agent jobs can still run.")) return;
  button.disabled = true;
  try { await act(action); } finally { button.disabled = false; }
});
$("login-form").onsubmit = async event => {
  event.preventDefault(); const button = event.submitter; button.disabled = true;
  try {
    const result = await api("/api/login", {password: $("password").value, ...(setup ? {code: $("setup-code").value} : {})});
    csrf = result.csrf; $("password").value = ""; $("setup-code").value = "";
    $("login").hidden = true; $("workspace").hidden = false; await refresh();
  } catch (error) { $("login-error").textContent = error.message; }
  finally { button.disabled = false; }
};
$("logout").onclick = async () => {
  try { await api("/api/logout", {}); location.reload(); } catch (error) { notify(error.message, true); }
};
$("task-form").onsubmit = async event => {
  event.preventDefault(); const button = event.submitter; button.disabled = true;
  try {
    const result = await act("task", {title: $("task-title").value, prompt: $("task-prompt").value,
      mode: $("task-mode").value, resume_run: $("task-resume").value || null});
    if (result) { $("task-title").value = ""; $("task-prompt").value = ""; $("task-resume").value = ""; }
  } finally { button.disabled = false; }
};
$("guidance-form").onsubmit = async event => { event.preventDefault(); await act("guidance", {text: $("guidance").value}); };
$("policy-toggle").onclick = () => {
  const audit = !snapshot?.preferences?.audit_only;
  if (confirm(`Switch future runs to ${audit ? "READ ONLY (also prevents clock publication)" : "PUBLISH when safe"}?`)) act("policy", {audit_only: audit});
};
$("latest-open").onclick = () => { if (snapshot?.latest?.run_id) openRun(snapshot.latest.run_id).catch(error => notify(error.message, true)); };
$("close-run").onclick = () => { selectedRun = null; $("run-detail").hidden = true; };
$("follow-up").onclick = () => { tab("agents"); $("task-resume").value = selectedRun;
  $("task-title").value = `Follow-up: ${selectedRun}`; $("task-prompt").focus(); $("agents").scrollIntoView({behavior: "smooth"}); };
$("journal-refresh").onclick = async () => {
  try { $("journal").textContent = (await api("/api/journal")).text; } catch (error) { notify(error.message, true); }
};
$("repo-refresh").onclick = () => loadRepository().catch(error => notify(error.message, true));
const presets = {
  repair: ["Repair automation", "Investigate the current automation-health findings and recent failed runs. Identify and fix the root cause where possible, preserve last-good data, add focused regression tests, publish verified repairs when safe, and report any upstream source blocks honestly.", "publish"],
  feature: ["Website improvement", "Implement this website improvement:\n\nOutcome:\n\nAffected pages:\n\nAcceptance criteria:\n\nUse the existing design and source contracts, add focused tests, verify the rendered result, publish when safe and confirm it is live.", "publish"],
  audit: ["Read-only diagnosis", "Read the current automation status, recent reports and live coverage. Diagnose the highest-impact unresolved issue and report concrete evidence and a recommended repair. Do not edit the checkout or publish anything.", "read_only"]
};
document.querySelectorAll("[data-preset]").forEach(button => button.onclick = () => {
  const [title, prompt, mode] = presets[button.dataset.preset];
  $("task-title").value = title; $("task-prompt").value = prompt; $("task-mode").value = mode;
});
(async () => {
  try {
    const auth = await api("/api/auth"); csrf = auth.csrf || ""; setup = auth.setup;
    $("setup-help").hidden = !setup;
    $("password").autocomplete = setup ? "new-password" : "current-password";
    if (setup) $("password").minLength = 12;
    $("login").hidden = auth.authenticated; $("workspace").hidden = !auth.authenticated;
    if (auth.authenticated) await refresh();
  } catch (error) { $("login-error").textContent = error.message; }
})();
setInterval(refresh, 5000);
