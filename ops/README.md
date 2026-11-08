# Persistent coverage watchdog

The owner-authorized external watchdog is separate from GitHub's REVIEW-mode
editor. It reads `SKILL.md`, `ops/watchdog-context.md` and its previous local
report on each fresh Copilot session. It can publish relevant verified fixes
when authenticated, but defaults to read-only if GitHub credentials are absent
or a deployment/editor workflow is active.

## Deployment layout

Use a dedicated nonroot service user. Machine access, container/host details,
retained checkouts and session IDs belong in the locally excluded
`LOCAL-AUTOMATION.md` supplied by the operator. Do not publish that handoff.

| Location | Purpose |
|---|---|
| `~/projects/f1-commentary-watchdog` | Dedicated checkout, never the interactive workspace |
| `~/.local/share/f1-watchdog/venv` | Python 3.12 and optional source/PDF/timing dependencies |
| `~/.local/state/f1-watchdog/latest.json` | Last run status, authentication/publication mode, report path |
| `~/.local/state/f1-watchdog/runs/<UTC timestamp>/` | Per-run report, agent output and CLI logs |
| `~/.local/state/f1-watchdog/memory.md` | Revalidated operational lessons between fresh sessions |
| `~/projects/f1-commentary-scheduler` | Separate clean checkout for the deterministic clock |
| `~/.local/state/f1-watchdog/scheduler.json` | Durable deadlines, attempts, live evidence and failures |
| `~/.config/systemd/user/f1-watchdog.service` | On-demand bounded AI repair worker |
| `~/.config/systemd/user/f1-calendar.{service,timer}` | One-minute deterministic calendar clock |

The calendar timer ticks every minute, without randomized delay. It reads the
latest source calendar, including each session's date and UTC offset. User
lingering keeps it running after logout/reboot. `Persistent=true` catches missed
ticks; durable per-session records prevent duplicate dispatches. The legacy
hourly `f1-watchdog.timer` must remain disabled.

| Trigger | Policy |
|---|---|
| Before every session | AI review eligible at T-105 minutes; fresh deterministic collection at T-60, publication deadline T-30 |
| Session finish | Poll every 2 minutes from estimated end minus 10 minutes; races start polling at T+60 to cover short dry races |
| Expected durations | Practice/qualifying 60 min, Sprint Qualifying 45, Sprint 30, race 120; final grid from qualifying end |
| Delayed results | Continue until a validated classification is visible live; after six overdue hours back off to 15-minute polling |
| Source/editorial gaps | Deterministic retries hourly, then bounded AI repair when permitted; never invent missing information |
| Host heartbeat | Update health issue at least every 30 minutes; independent GitHub job alerts after 90 minutes without a heartbeat |

Session durations are estimates, not declarations that a red-flagged session
has finished. GitHub dispatch/Pages is still best-effort: missed T-30 deadlines
are recorded and alerted, never reported as successful freshness. Rapid dispatches
skip historical/telemetry work; ordinary scheduled builds retain those collectors.
The editor and publisher use separate locks because the editor only submits PRs.
All queued deployments, including pushes, fetch current `main` before collecting
and check that the requested commit is still an ancestor. Otherwise a preceding
build's bot data commit can conflict with the next build's generated timestamps.
The 30-minute collection-to-deadline margin accommodates the existing two
ten-minute Pages deployment attempts; a real smoke deployment exercised that
timeout/retry path. It is not a guarantee against a prolonged GitHub outage.

Every build publishes `/automation-health.json`: validated classification
fingerprints, collector outcomes, news review status, expected FIA/Pirelli/tyre
deadlines and standings checkpoints. New FIA hashes require an explicit reviewed
receipt, not merely a screenshot. Expected-source gaps ask for verification;
they are not proof that the FIA has already released a document.
`data/collection_status.json` retains each collector's last actual outcome and
scope. A quick results-only build cannot clear a failed news/FIA check merely
by skipping that collector; a real successful retry is required.

The clock never edits source/data itself: it dispatches the existing tested
publisher and verifies the live evidence. Its separate checkout cannot be
contaminated by unfinished agent edits. The repair worker retains its own lock
and 45-minute budget. The clock keeps collecting if Copilot is unavailable.
Logs/state are owner-only.

The wrapper enforces a finalization reserve, rather than relying only on prompt
deadlines. After 35 minutes of a normal 45-minute run it stops that agent process
group, captures retained-work evidence in `interruption.json`, and resumes the
same conversation once with a finalization-only instruction. Setup and shutdown
time count against the original deadline. The final turn must validate and finish
existing work or record an explicit blocker, not restart research or wait for
Pages. Existing authority and writer checks still apply; failed validation never
authorizes a push. Both phases append to `agent.log`, and any provisional report
is preserved as `report-before-finalization.json`. A second timeout remains a
visible failure with fresh retained-work evidence, never automatic success.

A completed calendar check exits successfully even when it detects coverage
findings, overdue publication or an agent blocker. These remain in `errors`,
drive retries/health-issue alerts, and set `health_status` to `attention`; service
success is not a claim of complete coverage. Actual execution failures (repository,
API, live-evidence access or heartbeat errors) also populate `execution_errors`,
set `health_status` to `error`, and exit nonzero. A clean check is `healthy`.

`preferences.json` retains `audit_only` and adds `health_issue` (the issue number).
`agent_blocked_reason`, when present, prevents repeated paid agent attempts and
is prominently reported. Clear it only after resolving the underlying failure
and observing a successful unattended smoke run. Read-only mode also suppresses
clock dispatches. Repository variable `F1_WATCHDOG_HEALTH_ISSUE` selects the
operator dashboard issue for the independent monitor.

## Authentication

Authenticate **on the host as the service user**; do not copy another machine's
credentials, commit tokens or paste them into chat:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
copilot login --device-code
```

Copilot and `gh` authentication are distinct. Copilot was already authenticated
when provisioning began; `gh` was not. Each run detects the current state.
Without `gh`, public metadata and page audits can run, but fixes/publication are
blocked and the status explicitly records `READ_ONLY` and the authentication
requirement. A successful read-only audit is not a successful repair.

If the agent log says the required virtualenv interpreter needs approval, the
run is blocked even when the timer and GitHub authentication work. Preserve the
unpublished commit/diff and resolve the CLI permission request interactively on
the host; do not use unrestricted paths or an alternate interpreter to bypass
the denial. On 1 October, this left valid Sepang corrections in the checkout
while GitHub's deterministic deploys continued. The subsequent audit integrated
that work separately; a green deployment does not clear the agent's permission
problem.

On 6 November the paused timer was discovered still stopped. The stale checkout
was retained as `~/projects/f1-commentary-watchdog-retained-20261106` and replaced
with a fresh clone. Both a scoped virtualenv path and an exact interpreter tool
approval were tested; unattended execution was still denied. The automatic CLI
update to 1.0.106 did not clear it. Do not equate timer recovery with permission
recovery: the calendar collector can run, while AI publication remains explicitly
blocked until the operator resolves that approval interactively.

The subsequent approval investigation identified the separate path gate:
`venv/bin/python3` resolves to `/usr/bin/python3.12`. The CLI checks the resolved
target, not just the virtualenv path. An interactive exact-file approval works
only in that process; resuming it unattended does not retain the grant.
The owner therefore authorized adding `/usr/bin`. The wrapper grants the
resolved interpreter's parent directory on every fresh invocation, alongside
the virtualenv directory and explicit interpreter tool rule. It does not grant
`/usr`, `/`, unrestricted paths, or an alternate interpreter. Existing
`ProtectSystem=strict` keeps system binaries read-only; the denied host-management
commands are unchanged. Recheck this canonical path if the runtime moves.
The fix was verified with a fresh unattended CLI using actual wrapper arguments
under service-equivalent restrictions, executing the interpreter and importing
the PDF dependencies. The blocker was removed only after independent evidence
verification; a subsequent full PUBLISH run completed and deployed a repair.
An interactive success, CLI upgrade or timer restart alone is not that proof.

## Operations

Successful recovery reports may explicitly name `resolved_runs` and a verified
`resolution_basis`. The wrapper propagates only completed PUBLISH-mode repairs
to original finished runs/tasks, preserving old reports and process outcomes
with `resolution.json` and `previous_status`. A pending deployment cannot resolve
the original task until independent publication verification completes. Queued,
running and cancelled jobs are never silently overwritten.

Publication waits finish automatically: the calendar reconciles completed
blocked reports with the actually live successful Pages run, verifies commit
ancestry and affected rendered routes, then records `publication.json` and updates
the run/task to `fixed`. Original audit reports and source limitations are retained.
Until independently verified the state is `waiting_publication`, not success.
This also applies when an agent labels its report `fixed` but explicitly says
publication is unconfirmed; the label cannot override the missing live evidence.
Older inconsistent reports are reconciled without overwriting the original audit.
This costs no additional agent invocation and survives restarts. A later
descendant deployment can publish an earlier repair too.

Publisher conflicts before an operator job starts remain queued with automatic
five-minute retry (`waiting`, not a failed audit). If an agent explicitly defers
publication mid-task, the task resumes its conversation after five minutes, up
to three automatic continuations. Credential/permission failures, interrupted
edits and unrelated blocked findings are not blindly retried or marked successful.

Run history and the run inspector show a recovery card with the cause, next
step, and whether recovery is automatic or requires operator action. **Resume
safely** queues a focused continuation after confirmation and deduplicates
existing queued/running follow-ups. It checks prior publication before finishing
retained work, instead of repeating a full audit. Login/approval blocks link to
the existing authenticated browser terminal and explain the required action;
the UI never clears permission blockers or requests credentials. Verified
publication evidence appears above the preserved original report.

### Browser control room

`ops/watchdog_web.py` adds a private, standalone HTTPS application; it is not
part of the public Pages site. The Overview shows calendar freshness, deadlines,
source findings, worker state, latest outcome and service journal. Agent workspace
accepts prompted repair/development jobs and follow-up instructions. Run history
provides reports and auto-refreshing output; Repository shows status, recent
commits and a bounded tracked-code diff. Operating policy edits persistent guidance
and read-only/publish preference without dropping other preference fields.

Jobs are durable files under `tasks/` in the existing state directory, with
operator events in `operator-events.jsonl`. The web dispatcher checks every five
seconds; the existing watchdog claims jobs under its writer lock, never starting
concurrent checkout writers. Follow-ups resume the selected Copilot conversation
after it finishes. Instructions do not enter a live running session. Publishing
jobs wait and retry after five minutes when policy, authentication or an active
GitHub writer prevents publication. Read-only jobs remain read-only. Cancel only
affects queued jobs; Stop preserves unfinished edits. Pausing the calendar does
not cancel explicitly queued jobs.

Website features can be implemented, tested and published entirely from prompts
in the browser. Agents retain their existing 45-minute budget, source contracts,
service hardening, path/domain permissions and publication checks. Operator
service installation, credentials and changes to their own authority are not
delegated to those agents. Use the existing authenticated browser terminal for
exceptional operator maintenance, not a second concurrent checkout writer.

The worker's 45-minute limit includes setup, not just model execution. Each
prompt supplies absolute UTC edit and finish checkpoints, asks for an early
provisional report, and caps deployment waiting at two minutes. If publication
is still pending, report its commit/run URL for a later check instead of waiting
until the worker is killed. A timeout cannot be ruled out (tools and upstream
services can stall), so the wrapper also writes a blocked fallback report with
HEAD and retained checkout state when the agent exits without one. A fallback
is not proof of publication; the process status still records the failure.
Existing reports are preserved. Changes to the installed worker require
operator installation; repository publication alone does not update that copy.

Install reviewed application files outside the worker checkout:

```bash
python3 ops/install_web.py --origin https://<operator-host>:8443
```

The installer checks that the worker is idle and queue-capable, installs reviewed
code and the service, creates owner-only configuration, and starts the web UI.
It preserves existing authentication/certificates and prints the public certificate
fingerprint. It writes `F1_WEB_ORIGIN` into the private file
`~/.config/f1-watchdog-web/environment`. Pre-supply `cert.pem` and `key.pem` there
for trusted LAN TLS, otherwise it generates a long-lived self-signed certificate
with the correct hostname/IP subject alternative name. Verify its fingerprint
before accepting the browser warning. The listener binds to container loopback port
8443; route that port through the container's existing LAN proxy mechanism.
Do not open an unauthenticated listener, publish it on the Internet, or modify
the TrueNAS management webserver. Certificate renewal is an operator responsibility.

```bash
systemctl --user daemon-reload
systemctl --user enable --now f1-watchdog-web.service
~/.local/share/f1-watchdog/venv/bin/python3 \
  ~/.local/share/f1-watchdog/web/watchdog_web.py --setup-code
```

Generate the first-login code only inside the existing authenticated operator
terminal; the deployment's `f1-web-access` convenience launcher does this.
The code expires in 30 minutes and is single-use. The browser exchanges it for
a password of at least 12 characters; only a salted scrypt hash is stored.
HTTPS-only, HttpOnly, SameSite cookies expire after 12 hours; restarts invalidate
sessions. Mutation endpoints require a session, CSRF token and the configured
Host/Origin. Failed logins are throttled, request/log sizes are bounded, and
all source/report/prompt content is displayed as text, not executable markup.
Keep the config directory owner-only and outside the agent's writable paths.
No new GitHub/Copilot credentials are created or copied.

Install `agent_queue.py` alongside the worker's updated `watchdog.py` before
enabling this service. Updating a checkout alone does not update the installed UI.
After installation verify authenticated status/logs, an actual bounded read-only
agent job, and that `f1-calendar.timer` remains enabled with fresh ticks.

### Curses console (recommended)

Use the operator's existing terminal or SSH connection (see the private local
handoff) and run:

```bash
~/.local/bin/f1-watchdog
```

The console refreshes service/timer status and run history automatically.

| Key | Control |
|---|---|
| Up / Down | Select a run |
| Enter / `l` / `j` | Read report / follow agent log / view service journal |
| `h` | Calendar health, pending deadlines and publication/repair blockers |
| `a` | Fetch a read-only snapshot of GitHub automation and open PRs |
| `s` / `x` | Start now / confirm stop of current audit |
| `p` / `r` | Pause / resume future scheduling (persists across reboot) |
| `m` | Switch next-run read-only/publish preference |
| `g` | Edit persistent next-run guidance; Ctrl-G saves, Esc cancels |
| `i` | Confirm interactive takeover: pause timer, stop writer, resume conversation |
| `?` / `q` | Help / quit console without stopping automation |

Log viewers support arrows, Page Up/Down, Home/End and `f` to toggle following.
The console shows stopped-but-unfinalized runs as interrupted rather than running.
Guidance and policy changes apply **only to future runs**, not to an active agent.
Publication still depends on authentication and remote-writer checks.
Interactive takeover holds the watchdog lock; use `/exit` to return to the console,
then `r` when ready to restart scheduling. Older runs without recorded session
IDs open the CLI resume picker. New runs record their session IDs automatically.

The console runs as the human operator, outside the restricted agent service.
Its installed copy is `~/.local/share/f1-watchdog/watchdog_console.py` with launchers
`/usr/local/bin/f1-watchdog` and `~/.local/bin/f1-watchdog`; updating these files
does not restart the watchdog.
The `f1-watchdog` tmux terminal is a convenience entry in the existing browser menu;
after closing that terminal or a reboot, the launcher remains available from any
shell. No extra network listener or browser credential is added.

### Shell commands

```bash
systemctl --user status f1-calendar.timer --no-pager
systemctl --user list-timers f1-calendar.timer --all --no-pager
systemctl --user start --no-block f1-watchdog.service
journalctl --user -u f1-watchdog.service -n 60 --no-pager
python3 -m json.tool ~/.local/state/f1-watchdog/latest.json
systemctl --user stop f1-watchdog.service
systemctl --user disable --now f1-calendar.timer
```

One-off read-only audit:

```bash
~/.local/share/f1-watchdog/venv/bin/python3 \
  ~/projects/f1-commentary-watchdog/ops/watchdog.py --audit-only
```

The local lock does **not** lock GitHub Actions. The agent must recheck remote
writers before publication, fetch/reconcile latest main and preserve concurrent
data updates. It may defer rather than overwrite. Do not launch another writer
against this checkout while the service is running.

The service is non-root, has no privilege escalation and mounts the system
read-only with narrowly scoped writable checkout/state/cache directories. CLI
path verification remains enabled. This is not a guarantee of isolation from
everything owned by the user: the agent still has powerful shell tools and the
user's authorized GitHub identity. Its prompt explicitly forbids unrelated
service/credential/security changes. Audit the reports and GitHub commits.

Repository updates refresh the checkout on each clean-main run. Unit or
dependency changes require explicit operator installation; the agent is not
authorized to reconfigure its own scheduler or authority contract. Logs are
retained for diagnosis; inspect disk usage periodically and remove only reviewed,
completed run directories when retention cleanup is needed.

Install reviewed `f1-calendar.service` and `f1-calendar.timer` into
`~/.config/systemd/user/`, then run `systemctl --user daemon-reload`,
`systemctl --user disable --now f1-watchdog.timer` and
`systemctl --user enable --now f1-calendar.timer`. Create the separate scheduler
clone first. Keep the console's installed copy in sync. Verify `scheduler.json`,
the next timer tick, a real dispatch and the resulting live health endpoint.
Never leave a maintenance pause without either restoring it or a visible blocker
in the health issue.
