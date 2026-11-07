#!/usr/bin/env python3
"""Private HTTPS control room for the existing watchdog and calendar services."""
import argparse
from collections import deque
import datetime as dt
import fcntl
import hashlib
import hmac
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
from pathlib import Path
import secrets
import ssl
import subprocess
import threading
import time
from urllib.parse import urlsplit

try:
    from . import agent_queue as queue
    from . import watchdog_console as console
    from . import run_recovery
except ImportError:
    import agent_queue as queue
    import watchdog_console as console
    import run_recovery

CONFIG = Path.home() / ".config/f1-watchdog-web"
ASSETS = Path(__file__).with_name("web")
COOKIE = "f1_control"
LOGGER = logging.getLogger("f1-control")


def password_record(password):
    if not isinstance(password, str) or not 12 <= len(password) <= 1024:
        raise ValueError("Use a password of 12-1024 characters")
    salt = secrets.token_hex(16)
    return {"salt": salt, "hash": hashlib.scrypt(
        password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()}


def password_matches(password, record):
    if not isinstance(password, str) or len(password) > 1024:
        return False
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(record["salt"]),
                            n=16384, r=8, p=1).hex()
    return hmac.compare_digest(digest, record["hash"])


class ControlRoom:
    def __init__(self, state, config):
        self.state, self.config = state, config
        self.mutex = threading.RLock()
        self.sessions = {}
        self.failures = deque()
        self.last_dispatch = 0
        self.dispatch_error = None
        self.dispatch_checked = None
        self.stopping = threading.Event()

    def audit(self, action, detail):
        self.state.mkdir(parents=True, exist_ok=True)
        with (self.state / "operator-events.jsonl").open("a") as handle:
            handle.write(json.dumps({"at": queue.now(), "action": action, "detail": detail}) + "\n")

    def login(self, data):
        with self.mutex:
            current = time.monotonic()
            while self.failures and self.failures[0] < current - 300:
                self.failures.popleft()
            if len(self.failures) >= 10:
                raise PermissionError("Too many login attempts; try again in five minutes")
            credentials = self.config / "password.json"
            if credentials.exists():
                valid = password_matches(data.get("password"), console.read_json(credentials))
            else:
                setup = console.read_json(self.config / "setup.json")
                valid = (setup.get("expires", 0) > time.time()
                         and isinstance(data.get("code"), str)
                         and hmac.compare_digest(
                             hashlib.sha256(data["code"].encode()).hexdigest(),
                             setup.get("digest", "")))
                if valid:
                    queue.save(credentials, password_record(data.get("password")))
                    (self.config / "setup.json").unlink()
            if not valid:
                self.failures.append(current)
                raise PermissionError("Invalid password or expired setup code")
            self.failures.clear()
            token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            self.sessions = {key: value for key, value in self.sessions.items()
                             if value["expires"] > time.monotonic()}
            if len(self.sessions) >= 100:
                self.sessions.pop(next(iter(self.sessions)))
            self.sessions[token] = {"csrf": csrf, "expires": time.monotonic() + 12 * 3600}
            self.audit("login", "operator")
            return token, csrf

    def session(self, header):
        parsed = cookies.SimpleCookie()
        try:
            parsed.load(header or "")
        except cookies.CookieError:
            return None, None
        token = parsed[COOKIE].value if COOKIE in parsed else None
        with self.mutex:
            session = self.sessions.get(token)
            if session and session["expires"] > time.monotonic():
                return token, session
        return None, None

    def snapshot(self):
        errors = []

        def read(name):
            try:
                return console.read_json(self.state / name)
            except (OSError, ValueError) as error:
                errors.append(f"{name}: {error}")
                return None

        units = {}
        for unit in (console.SERVICE, console.TIMER, "f1-calendar.service"):
            try:
                units[unit] = console.properties(unit)
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
                errors.append(f"{unit}: {error}")
        latest = read("latest.json")
        if (latest and latest.get("status") == "running"
                and units.get(console.SERVICE, {}).get("ActiveState")
                not in ("active", "activating", "deactivating")):
            latest = dict(latest, status="interrupted")
        history = []
        for path in console.runs(self.state)[:60]:
            try:
                status, mode = console.run_status(
                    path, latest or {}, units.get(console.SERVICE, {}).get("ActiveState"))
                record = console.read_json(path / "status.json")
                if not record and latest and latest.get("run_id") == path.name:
                    record = latest
                history.append({"run_id": path.name, "status": status, "mode": mode,
                                "summary": record.get("summary") or record.get("error"),
                                "started_at": record.get("started_at"),
                                "finished_at": record.get("finished_at"),
                                "task_title": record.get("task_title"),
                                "recovery": run_recovery.explain(
                                    dict(record, status=status), console.read_json(path / "report.json"))})
            except (OSError, ValueError) as error:
                errors.append(f"Run {path.name}: {error}")
        guidance = self.state / "operator-guidance.txt"
        clock = read("scheduler.json")
        checked = clock.get("checked_at") if clock else None
        stale = True
        if checked:
            try:
                stale = (dt.datetime.now(dt.timezone.utc) -
                         dt.datetime.fromisoformat(checked)).total_seconds() > 180
            except (TypeError, ValueError):
                errors.append("Invalid scheduler checked_at")
        if self.dispatch_error:
            errors.append(f"Task dispatcher: {self.dispatch_error}")
        return {"at": queue.now(), "units": units, "latest": latest, "scheduler": clock,
                "scheduler_stale": stale, "runs": history, "tasks": queue.jobs(self.state)[-100:],
                "preferences": read("preferences.json"),
                "guidance": guidance.read_text() if guidance.exists() else "",
                "events": console.read_tail(self.state / "operator-events.jsonl", 65536),
                "dispatcher_checked_at": self.dispatch_checked, "errors": errors}

    def run_path(self, identity):
        if not queue.RUN_ID.fullmatch(identity):
            raise ValueError("Invalid run ID")
        path = self.state / "runs" / identity
        if path.is_symlink() or not path.is_dir():
            raise FileNotFoundError("Run not found")
        return path

    def action(self, action, data):
        with self.mutex:
            if action == "recover":
                identity = data.get("run_id")
                if not isinstance(identity, str):
                    raise ValueError("Run ID required")
                directory = self.run_path(identity)
                record = console.read_json(directory / "status.json")
                latest = console.read_json(self.state / "latest.json")
                if not record and latest.get("run_id") == identity:
                    record = latest
                recovery = run_recovery.explain(record, console.read_json(directory / "report.json"))
                if not recovery or recovery.get("action") != "recover":
                    raise ValueError("This run does not need an agent recovery; inspect its next step")
                if data.get("confirmed") is not True:
                    raise ValueError("Confirm recovery before queuing a continuation")
                existing = next((job for job in queue.jobs(self.state)
                                 if identity in (job.get("resume_run"), job.get("recovery_run"))
                                 and job["status"] in ("queued", "running", "waiting_publication")), None)
                if existing:
                    return {"task": existing, "message": "A continuation is already queued or running"}
                job = queue.enqueue(
                    self.state, run_recovery.prompt(identity),
                    "read_only" if record.get("mode") == "READ_ONLY" else "publish",
                    f"Recover {identity}", identity if record.get("session_id") else None)
                queue.update(self.state, job["id"], recovery_run=identity)
                result = {"task": job, "message": "Safe recovery queued; completed work will be checked before continuing"}
            elif action == "task":
                job = queue.enqueue(self.state, data.get("prompt"), data.get("mode", "publish"),
                                    data.get("title", ""), data.get("resume_run"))
                result = {"task": job}
            elif action == "cancel":
                result = {"task": queue.cancel(self.state, data.get("id"))}
            elif action == "guidance":
                text = data.get("text")
                if not isinstance(text, str) or len(text.encode()) > 16384:
                    raise ValueError("Guidance must be text of at most 16 KiB")
                console.save_private(self.state / "operator-guidance.txt", text)
                result = {"message": "Guidance saved for future invocations; active agent unchanged"}
            elif action == "policy":
                if not isinstance(data.get("audit_only"), bool):
                    raise ValueError("audit_only must be boolean")
                preference = console.read_json(self.state / "preferences.json")
                preference["audit_only"] = data["audit_only"]
                queue.save(self.state / "preferences.json", preference)
                result = {"message": "Future-run policy saved; existing authority limits still apply"}
            elif action == "start":
                console.systemctl("start", "--no-block", console.SERVICE)
                result = {"message": "Audit requested"}
            elif action == "stop":
                console.systemctl("stop", console.SERVICE, timeout=60)
                # The worker may have been killed before its finally block.
                with (self.state / "run.lock").open("a") as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    for job in queue.jobs(self.state):
                        if job["status"] == "running":
                            queue.update(self.state, job["id"], status="interrupted",
                                         error="Stopped by operator", finished_at=queue.now())
                result = {"message": "Agent stopped; unfinished work preserved. Scheduling unchanged"}
            elif action == "pause":
                console.systemctl("disable", "--now", console.TIMER)
                console.systemctl("stop", "f1-calendar.service", timeout=60)
                result = {"message": "Calendar paused. Explicitly queued tasks still run"}
            elif action == "resume":
                console.systemctl("enable", "--now", console.TIMER)
                result = {"message": "Calendar monitoring enabled"}
            else:
                raise ValueError("Unknown action")
            self.audit(action, {"task_id": result.get("task", {}).get("id"),
                                "message": result.get("message")})
            return result

    def dispatch(self):
        while not self.stopping.wait(5):
            try:
                with self.mutex:
                    self.dispatch_checked = queue.now()
                    active = console.properties(console.SERVICE).get("ActiveState")
                    if active not in ("active", "activating", "deactivating"):
                        queue.recover(self.state)
                    pending = any(job["status"] == "queued"
                                  and job.get("not_before", "") <= queue.now()
                                  for job in queue.jobs(self.state))
                    if pending and time.monotonic() - self.last_dispatch >= 60:
                        if active not in ("active", "activating", "deactivating"):
                            console.systemctl("start", "--no-block", console.SERVICE)
                            self.last_dispatch = time.monotonic()
                    self.dispatch_error = None
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
                self.dispatch_error = str(error)
                LOGGER.exception("Task dispatch failed")


class Handler(BaseHTTPRequestHandler):
    server_version = "F1-Control"

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    @property
    def app(self):
        return self.server.app

    def log_message(self, fmt, *args):
        LOGGER.info("%s %s", self.client_address[0], fmt % args)

    def send(self, code, payload, content_type="application/json", headers=None):
        raw = json.dumps(payload).encode() if content_type == "application/json" else payload
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; "
                         "style-src 'self'; img-src 'self'; connect-src 'self'; "
                         "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        try:
            path = urlsplit(self.path).path
            assets = {"/": ("index.html", "text/html; charset=utf-8"),
                      "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                      "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path in assets:
                name, kind = assets[path]
                return self.send(200, (ASSETS / name).read_bytes(), kind)
            if path == "/api/auth":
                _, session = self.app.session(self.headers.get("Cookie"))
                return self.send(200, {"authenticated": bool(session),
                                      "setup": not (self.app.config / "password.json").exists(),
                                      "csrf": session["csrf"] if session else None})
            _, session = self.app.session(self.headers.get("Cookie"))
            if not session:
                return self.send(401, {"error": "Sign in to view the control room"})
            if path == "/api/status":
                return self.send(200, self.app.snapshot())
            if path == "/api/repository":
                values = {}
                for key, args in (
                    ("status", ["status", "--short", "--branch"]),
                    ("commits", ["log", "-12", "--format=%h %ad %s", "--date=iso-strict"]),
                    ("diff", ["diff", "HEAD", "--", ".", ":!assets_src", ":!data"]),
                ):
                    result = subprocess.run(
                        ["git", "--no-pager", "-C", str(console.CHECKOUT), *args],
                        capture_output=True, text=True, timeout=15)
                    if result.returncode:
                        raise RuntimeError(result.stderr.strip())
                    values[key] = console.clean(result.stdout[:200000])
                    if len(result.stdout) > 200000:
                        values[key] += "\n[Output truncated at 200000 characters]"
                return self.send(200, values)
            if path == "/api/journal":
                result = subprocess.run(
                    ["journalctl", "--user", "-u", console.SERVICE, "-u", "f1-calendar.service",
                     "-n", "180", "--no-pager", "-o", "short-iso"],
                    capture_output=True, text=True, timeout=10)
                if result.returncode:
                    raise RuntimeError(result.stderr.strip())
                return self.send(200, {"text": console.clean(result.stdout)})
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[:2] == ["api", "runs"]:
                directory = self.app.run_path(parts[2])
                if parts[3] == "report":
                    report = directory / "report.json"
                    record = console.read_json(directory / "status.json")
                    latest = console.read_json(self.app.state / "latest.json")
                    if not record and latest.get("run_id") == directory.name:
                        record = latest
                    value = console.read_json(report) if report.exists() else {
                        "status": "pending", "summary": "No final report yet"}
                    return self.send(200, {"report": value, "status": record,
                                          "publication": console.read_json(directory / "publication.json"),
                                          "recovery": run_recovery.explain(record, value)})
                if parts[3] == "log":
                    return self.send(200, {"text": console.read_tail(directory / "agent.log")})
            self.send(404, {"error": "Not found"})
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            LOGGER.exception("Read request failed")
            self.send(500, {"error": str(error)})

    def do_POST(self):
        try:
            if self.headers.get("Transfer-Encoding"):
                return self.send(400, {"error": "Transfer encoding is not supported"})
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 100000:
                return self.send(413, {"error": "Request must be 1-100000 bytes"})
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.send(415, {"error": "JSON required"})
            origin = self.headers.get("Origin")
            if origin and origin != "https://" + self.server.allowed_host:
                return self.send(403, {"error": "Cross-origin request rejected"})
            if self.headers.get("Host") != self.server.allowed_host:
                return self.send(403, {"error": "Unexpected host"})
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("JSON object required")
            path = urlsplit(self.path).path
            if path == "/api/login":
                token, csrf = self.app.login(data)
                return self.send(200, {"csrf": csrf}, headers={
                    "Set-Cookie": f"{COOKIE}={token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=43200"})
            token, session = self.app.session(self.headers.get("Cookie"))
            if not session:
                return self.send(401, {"error": "Session expired; sign in again"})
            if not hmac.compare_digest(self.headers.get("X-CSRF-Token", ""), session["csrf"]):
                return self.send(403, {"error": "Invalid CSRF token"})
            if path == "/api/logout":
                with self.app.mutex:
                    self.app.sessions.pop(token, None)
                return self.send(200, {"message": "Signed out"}, headers={
                    "Set-Cookie": f"{COOKIE}=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0"})
            if not path.startswith("/api/actions/"):
                return self.send(404, {"error": "Not found"})
            self.send(200, self.app.action(path.removeprefix("/api/actions/"), data))
        except PermissionError as error:
            self.send(403, {"error": str(error)})
        except (ValueError, FileNotFoundError, BlockingIOError) as error:
            self.send(400, {"error": str(error)})
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            LOGGER.exception("Operator action failed")
            self.send(500, {"error": str(error)})


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 32

    def __init__(self, address, app, allowed_host):
        self.app, self.allowed_host = app, allowed_host
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(address, Handler)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()

    def get_request(self):
        request, address = super().get_request()
        request.settimeout(10)
        try:
            request = self.tls.wrap_socket(request, server_side=True)
        except (OSError, TimeoutError):
            request.close()
            raise
        return request, address


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=console.STATE)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--origin", help="Exact browser origin, e.g. https://host:8443")
    parser.add_argument("--setup-code", action="store_true",
                        help="Generate a 30-minute first-login code (never resets an existing password)")
    args = parser.parse_args()
    os.umask(0o077)
    args.config.mkdir(parents=True, exist_ok=True)
    if args.setup_code:
        if (args.config / "password.json").exists():
            parser.error("A password is already configured")
        code = secrets.token_urlsafe(24)
        queue.save(args.config / "setup.json", {
            "digest": hashlib.sha256(code.encode()).hexdigest(), "expires": time.time() + 1800})
        print("First-login setup code (expires in 30 minutes):\n" + code)
        return
    origin = urlsplit(args.origin or "")
    if origin.scheme != "https" or not origin.netloc or origin.path or origin.query or origin.fragment:
        parser.error("--origin must be an HTTPS origin with no path")
    app = ControlRoom(args.state, args.config)
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.minimum_version = ssl.TLSVersion.TLSv1_2
    tls.load_cert_chain(args.config / "cert.pem", args.config / "key.pem")
    server = Server((args.host, args.port), app, origin.netloc)
    server.tls = tls
    thread = threading.Thread(target=app.dispatch, daemon=True)
    thread.start()
    LOGGER.info("Control room listening on %s:%s", args.host, args.port)
    try:
        server.serve_forever()
    finally:
        app.stopping.set()
        server.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
