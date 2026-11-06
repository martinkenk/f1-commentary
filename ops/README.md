# Persistent coverage watchdog

The owner-authorized external watchdog is separate from GitHub's REVIEW-mode
editor. It reads `SKILL.md`, `ops/watchdog-context.md` and its previous local
report on each fresh Copilot session. It can publish relevant verified fixes
when authenticated, but defaults to read-only if GitHub credentials are absent
or a deployment/editor workflow is active.

## Installed host layout

Host: `ssh 192.168.110.151 -p2222`, user `martin`.

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

`preferences.json` retains `audit_only` and adds `health_issue` (the issue number).
`agent_blocked_reason`, when present, prevents repeated paid agent attempts and
is prominently reported. Clear it only after resolving the underlying failure
and observing a successful unattended smoke run. Read-only mode also suppresses
clock dispatches. Issue #115 is the installed operator dashboard; repository
variable `F1_WATCHDOG_HEALTH_ISSUE` selects it for the independent monitor.

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

## Operations

### Curses console (recommended)

Open **https://192.168.110.151:7681/** and select the **f1-watchdog** terminal.
Alternatively, run `f1-watchdog` in a shell inside the web terminal, or connect
directly with:

```bash
ssh -t -p 2222 192.168.110.151 ~/.local/bin/f1-watchdog
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
