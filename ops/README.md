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
| `~/.config/systemd/user/f1-watchdog.{service,timer}` | Installed copies of these units |

The timer runs hourly at **minute 37 UTC**, with up to two minutes of jitter.
`Persistent=true` catches up after downtime. User lingering starts the timer at
boot and keeps it active after SSH logout. A local file lock prevents duplicate
runs; the service limits each agent to 45 minutes and kills remaining child
processes at 50 minutes. Logs/state are owner-only.

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
Its installed copy is `~/.local/share/f1-watchdog/watchdog_console.py` with launcher
`~/.local/bin/f1-watchdog`; updating these files does not restart the watchdog.
The `f1-watchdog` tmux terminal is a convenience entry in the existing browser menu;
after closing that terminal or a reboot, the launcher remains available from any
shell. No extra network listener or browser credential is added.

### Shell commands

```bash
systemctl --user status f1-watchdog.timer --no-pager
systemctl --user list-timers f1-watchdog.timer --all --no-pager
systemctl --user start --no-block f1-watchdog.service
journalctl --user -u f1-watchdog.service -n 60 --no-pager
python3 -m json.tool ~/.local/state/f1-watchdog/latest.json
systemctl --user stop f1-watchdog.service
systemctl --user disable --now f1-watchdog.timer
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
