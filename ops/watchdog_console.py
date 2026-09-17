#!/usr/bin/env python3
"""Curses controls for the F1 watchdog, usable through SSH or the web terminal."""
import argparse
import curses
import curses.textpad
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import textwrap
import time
import uuid

HOME = Path.home()
STATE = HOME / ".local/state/f1-watchdog"
CHECKOUT = HOME / "projects/f1-commentary-watchdog"
SERVICE = "f1-watchdog.service"
TIMER = "f1-watchdog.timer"
ANSI = re.compile(r"\x1b\][^\x07]*(?:\x07|\x1b\\)|\x1b\[[0-?]*[ -/]*[@-~]")


def clean(text):
    text = ANSI.sub("", text)
    return "".join(c for c in text if c in "\n\t" or (c.isprintable() and c != "\x7f"))


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else {}


def read_tail(path, limit=512 * 1024):
    if not path.exists():
        return "No log has been written for this run yet."
    with path.open("rb") as handle:
        size = handle.seek(0, 2)
        handle.seek(max(0, size - limit))
        raw = handle.read()
    prefix = "[Showing the last 512 KiB]\n" if size > limit else ""
    return prefix + clean(raw.decode("utf-8", errors="replace"))


def save_private(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w") as handle:
        os.chmod(temporary, 0o600)
        handle.write(text)
    temporary.replace(path)


def systemctl(*args, timeout=8):
    result = subprocess.run(["systemctl", "--user", *args], capture_output=True,
                            text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or
                           f"systemctl exited {result.returncode}")
    return result.stdout.strip()


def properties(unit):
    result = systemctl("show", unit, "--property=ActiveState,SubState,UnitFileState,"
                       "NextElapseUSecRealtime,Result,MainPID")
    return dict(line.split("=", 1) for line in result.splitlines() if "=" in line)


def runs(state):
    directory = state / "runs"
    if not directory.exists():
        return []
    return sorted((p for p in directory.iterdir() if p.is_dir() and not p.is_symlink()
                   and re.fullmatch(r"\d{8}T\d{6}Z", p.name)), reverse=True)


def run_status(path, latest, active):
    record = read_json(path / "status.json")
    if not record and latest.get("run_id") == path.name:
        record = latest
    if not record:
        record = read_json(path / "report.json")
    status = record.get("status", "unfinished")
    if status == "running" and active not in ("active", "activating", "deactivating"):
        status = "interrupted"
    return status, record.get("mode", "?")


def resume_arguments(checkout, record):
    session_id = record.get("session_id")
    if session_id:
        uuid.UUID(session_id)
        return ["copilot", "-C", str(checkout), "--mode", "interactive", "--resume", session_id]
    return ["copilot", "-C", str(checkout), "--mode", "interactive", "--resume"]


def wrapped(text, width):
    result = []
    for line in clean(text).expandtabs(4).splitlines():
        result.extend(textwrap.wrap(line, max(1, width), replace_whitespace=False,
                                    drop_whitespace=False) or [""])
    return result or ["(empty)"]


class Console:
    def __init__(self, screen, state=STATE, checkout=CHECKOUT):
        self.screen, self.state, self.checkout = screen, state, checkout
        self.history, self.selected = [], 0
        self.latest, self.service, self.timer = {}, {}, {}
        self.message = ""
        self.refreshed = 0
        self.screen.timeout(500)
        try:
            curses.curs_set(0)
        except curses.error:
            pass  # Some terminals do not expose cursor visibility controls.

    def put(self, y, text, attr=0, x=1):
        height, width = self.screen.getmaxyx()
        if 0 <= y < height and x < width - 1:
            try:
                self.screen.addnstr(y, x, clean(text).replace("\n", " "), width - x - 1, attr)
            except curses.error:
                pass  # A resize or a wide glyph at the right edge can invalidate the cell.

    def refresh(self):
        chosen = self.history[self.selected].name if self.history else None
        self.history = runs(self.state)
        self.selected = next((i for i, p in enumerate(self.history) if p.name == chosen), 0)
        self.latest = read_json(self.state / "latest.json")
        self.service, self.timer = properties(SERVICE), properties(TIMER)
        self.refreshed = time.monotonic()

    def confirm(self, message):
        self.screen.erase()
        for i, line in enumerate(wrapped(message, self.screen.getmaxyx()[1] - 4)):
            self.put(i + 2, line)
        self.put(self.screen.getmaxyx()[0] - 2, "Press y to confirm; any other key cancels.",
                 curses.A_BOLD)
        self.screen.refresh()
        self.screen.timeout(-1)
        try:
            return self.screen.getch() in (ord("y"), ord("Y"))
        finally:
            self.screen.timeout(500)

    def draw(self):
        self.screen.erase()
        height, width = self.screen.getmaxyx()
        self.put(0, "F1 WATCHDOG  |  automation & coverage", curses.A_BOLD)
        if height < 18 or width < 65:
            self.put(2, "Resize to at least 65 columns x 18 rows. q: quit")
            self.screen.refresh()
            return
        self.put(2, f"Agent: {self.service.get('ActiveState', '?')}/"
                 f"{self.service.get('SubState', '?')}  PID: {self.service.get('MainPID', '?')}"
                 f"  Last result: {self.service.get('Result', '?')}")
        self.put(3, f"Schedule: {self.timer.get('UnitFileState', '?')} / "
                 f"{self.timer.get('ActiveState', '?')}   "
                 f"Next: {self.timer.get('NextElapseUSecRealtime', 'not scheduled')}")
        preference = read_json(self.state / "preferences.json").get("audit_only", False)
        self.put(4, f"Next-run policy: {'READ ONLY' if preference else 'PUBLISH when safe'}"
                 f"   Last mode: {self.latest.get('mode', '?')}")
        self.put(5, self.latest.get("summary") or self.latest.get("error") or
                 self.latest.get("publication_deferred") or "Select a run to inspect its report or logs.")
        self.put(7, "RUN (UTC)             STATUS         MODE", curses.A_BOLD)
        visible = max(1, height - 14)
        start = max(0, self.selected - visible + 1)
        for row, path in enumerate(self.history[start:start + visible], 8):
            status, mode = run_status(path, self.latest, self.service.get("ActiveState"))
            attr = curses.A_REVERSE if start + row - 8 == self.selected else 0
            self.put(row, f"{path.name:21} {status:14} {mode}", attr)
        if not self.history:
            self.put(8, "No runs yet. Press s to start an audit.")
        self.put(height - 5, "s Start  x Stop  p Pause  r Resume  m Read-only/publish")
        self.put(height - 4, "Enter Report  l Log  j Journal  g Guidance  i Takeover")
        self.put(height - 3, "a GitHub  Up/Down Select  ? Help  q Quit (agent continues)")
        self.put(height - 1, self.message)
        self.screen.refresh()

    def viewer(self, title, loader, follow=False):
        offset = 0
        while True:
            height, width = self.screen.getmaxyx()
            text = loader()
            lines = wrapped(text, width - 3)
            page = max(1, height - 4)
            maximum = max(0, len(lines) - page)
            offset = maximum if follow else min(offset, maximum)
            self.screen.erase()
            self.put(0, title, curses.A_BOLD)
            for row, line in enumerate(lines[offset:offset + page], 2):
                self.put(row, line)
            self.put(height - 1, f"{offset + 1}/{len(lines)} "
                     f"{'[FOLLOW]' if follow else ''}  Up/Down PgUp/PgDn Home/End  f Follow  q Back")
            self.screen.refresh()
            key = self.screen.getch()
            if key in (ord("q"), 27):
                return
            if key in (curses.KEY_UP, curses.KEY_PPAGE, curses.KEY_HOME):
                follow = False
                offset = max(0, offset - (page if key == curses.KEY_PPAGE else 1))
                if key == curses.KEY_HOME:
                    offset = 0
            elif key in (curses.KEY_DOWN, curses.KEY_NPAGE):
                follow = False
                offset = min(maximum, offset + (page if key == curses.KEY_NPAGE else 1))
            elif key == curses.KEY_END:
                offset, follow = maximum, False
            elif key == ord("f"):
                follow = not follow

    def guidance(self):
        path = self.state / "operator-guidance.txt"
        current = path.read_text() if path.exists() else ""
        height, width = self.screen.getmaxyx()
        self.screen.erase()
        self.put(0, "GUIDANCE FOR FUTURE RUNS (not a message to the running agent)", curses.A_BOLD)
        self.put(1, "Ctrl-G saves; Esc cancels. Blank text clears guidance. Authority limits still apply.")
        window = curses.newwin(max(1, height - 4), max(1, width - 2), 3, 1)
        editor = curses.textpad.Textbox(window)
        lines = wrapped(current, width - 3) if current else []
        if len(lines) > height - 4:
            self.message = f"Guidance is too long for this window; enlarge it or edit {path}."
            return
        for row, line in enumerate(lines):
            window.addstr(row, 0, line[:width - 3])
        window.move(0, 0)
        cancelled = False

        def validate(key):
            nonlocal cancelled
            if key in (27, curses.KEY_RESIZE):
                cancelled = True
                return 7
            return key

        self.screen.refresh()
        try:
            curses.curs_set(1)
            text = editor.edit(validate).strip()
        finally:
            curses.curs_set(0)
        if not cancelled:
            if len(text.encode()) > 16384:
                raise ValueError("Guidance exceeds the 16 KiB limit")
            save_private(path, text + "\n" if text else "")
            self.message = "Guidance saved. It takes effect on the next run; the current run is unchanged."

    def takeover(self):
        if not self.confirm("Pause future audits, stop the current agent, and open an interactive "
                            "Copilot conversation for the selected run? Scheduling will remain paused "
                            "when you return; press r to resume it. Unfinished files will be preserved."):
            return
        systemctl("disable", "--now", TIMER)
        systemctl("stop", SERVICE, timeout=60)
        self.state.mkdir(parents=True, exist_ok=True)
        with (self.state / "run.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            selected = self.history[self.selected] if self.history else None
            record = read_json(selected / "status.json") if selected else {}
            if selected and self.latest.get("run_id") == selected.name:
                record = record or self.latest
            args = resume_arguments(self.checkout, record)
            curses.def_prog_mode()
            curses.endwin()
            try:
                subprocess.run(args, cwd=self.checkout, check=False)
            finally:
                curses.reset_prog_mode()
                self.screen.clear()
                self.screen.timeout(500)
        self.message = "Interactive session ended; scheduling remains PAUSED. Press r to resume."
        self.refreshed = 0

    def action(self, key):
        if key == ord("s"):
            systemctl("start", "--no-block", SERVICE)
            self.message = "Start requested; current policy applies. An already active run is not duplicated."
        elif key == ord("x") and self.confirm("Stop the current audit? Unfinished edits are preserved. "
                                             "Future scheduled audits remain enabled."):
            systemctl("stop", "--no-block", SERVICE)
            self.message = "Stop requested. The service will terminate the agent and its child processes."
        elif key == ord("p"):
            systemctl("disable", "--now", TIMER)
            self.message = "Future audits paused persistently. The current run is not stopped."
        elif key == ord("r"):
            systemctl("enable", "--now", TIMER)
            self.message = "Hourly scheduling enabled. A missed scheduled run may start immediately."
        elif key == ord("m"):
            path = self.state / "preferences.json"
            settings = read_json(path)
            audit = not settings.get("audit_only", False)
            if audit or self.confirm("Allow future runs to publish verified repairs when authenticated "
                                     "and no GitHub writer is active?"):
                settings["audit_only"] = audit
                save_private(path, json.dumps(settings, indent=2) + "\n")
                self.message = "Next-run policy saved. The running agent's mode is unchanged."
        elif key in (10, 13, curses.KEY_ENTER, ord("l")) and self.history:
            path = self.history[self.selected]
            if key == ord("l"):
                self.viewer(f"LIVE LOG - {path.name}", lambda: read_tail(path / "agent.log"), True)
            else:
                def report():
                    file = path / "report.json"
                    if not file.exists():
                        return "No report yet. Open the live log with l while the agent is running."
                    return json.dumps(read_json(file), indent=2, ensure_ascii=False)
                self.viewer(f"REPORT - {path.name}", report)
        elif key == ord("j"):
            def journal():
                result = subprocess.run(
                    ["journalctl", "--user", "-u", SERVICE, "-n", "250", "--no-pager", "-o", "short"],
                    capture_output=True, text=True, timeout=8)
                if result.returncode:
                    raise RuntimeError(result.stderr.strip())
                return result.stdout or "No journal entries."
            self.viewer("SERVICE JOURNAL", journal, True)
        elif key == ord("g"):
            self.guidance()
        elif key == ord("a"):
            snapshots = []
            for title, args in (
                ("RECENT AUTOMATION", ["run", "list", "--limit", "10", "--json",
                                      "databaseId,workflowName,status,conclusion,url"]),
                ("OPEN PULL REQUESTS", ["pr", "list", "--state", "open", "--limit", "15",
                                       "--json", "number,title,isDraft,url,headRefName"]),
            ):
                result = subprocess.run(
                    ["gh", *args, "--repo", "martinkenk/f1-commentary"],
                    capture_output=True, text=True, timeout=20)
                if result.returncode:
                    raise RuntimeError(result.stderr.strip() or "GitHub query failed")
                snapshots.append(title + "\n" + json.dumps(json.loads(result.stdout), indent=2))
            text = "\n\n".join(snapshots)
            self.viewer("GITHUB SNAPSHOT - reopen with a to refresh", lambda: text)
        elif key == ord("i"):
            self.takeover()
        elif key == ord("?"):
            self.viewer("HELP", lambda: HELP)
        self.refreshed = 0

    def loop(self):
        while True:
            try:
                if time.monotonic() - self.refreshed > 3:
                    self.refresh()
                self.draw()
                key = self.screen.getch()
                if key in (ord("q"), 27):
                    return
                if key == curses.KEY_UP:
                    self.selected = max(0, self.selected - 1)
                elif key == curses.KEY_DOWN:
                    self.selected = min(max(0, len(self.history) - 1), self.selected + 1)
                elif key != -1 and self.screen.getmaxyx()[0] >= 18 and self.screen.getmaxyx()[1] >= 65:
                    self.action(key)
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
                self.message = f"ERROR: {error}"
                self.put(self.screen.getmaxyx()[0] - 1, self.message)
                self.screen.refresh()
                if self.screen.getch() in (ord("q"), 27):
                    return


HELP = """Use this console in the private web terminal or over SSH.

s starts the systemd service. x stops only the current audit after confirmation.
p persistently disables the timer without stopping a running audit.
r enables the hourly timer; Persistent=true can catch up a missed run.
m toggles the next-run read-only/publish preference. Publication still requires
GitHub authentication and no active deployment/editor.

Select a historical run with Up/Down. Enter opens its report; l follows its log.
Use Page Up/Down and Home/End to scroll. f toggles following. q returns.
j shows recent systemd journal entries. Service state is authoritative if a
terminated run left a 'running' status record behind.
a fetches recent GitHub automation runs and open PRs (read-only snapshot).
Reopen it to refresh; it does not poll the GitHub API continuously.

g edits persistent guidance for FUTURE runs. Ctrl-G saves; Esc cancels.
This does not inject text into an active noninteractive agent. Clearing the
text removes the guidance. Do not include credentials.

i safely takes over interactively: it disables the timer, stops the service,
holds the watchdog lock and resumes the selected Copilot session. Older runs
without a recorded session ID open Copilot's resume picker. Use /exit to return.
The timer stays paused afterwards; press r when ready to resume automation.

q closes only this console. Audits and scheduling continue.
Existing logs are bounded to their last 512 KiB in the live viewer; full files
remain in ~/.local/state/f1-watchdog/runs/<timestamp>/agent.log.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE)
    parser.add_argument("--checkout", type=Path, default=CHECKOUT)
    args = parser.parse_args()
    # Long-lived tmux servers can predate the user's systemd session bus.
    runtime = os.environ.setdefault("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    os.environ.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path={runtime}/bus")
    try:
        curses.wrapper(lambda screen: Console(screen, args.state_dir, args.checkout).loop())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
