#!/usr/bin/env python3
"""Install reviewed control-room code as the existing nonroot operator user."""
import argparse
import ipaddress
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlsplit


def command(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", required=True, help="LAN HTTPS origin, e.g. https://host:8443")
    args = parser.parse_args()
    url = urlsplit(args.origin)
    if (url.scheme != "https" or not url.hostname or url.port != 8443 or url.username
            or url.password or url.path or url.query or url.fragment
            or not re.fullmatch(r"[a-zA-Z0-9.:-]+", url.hostname)):
        parser.error("Use an HTTPS hostname/IP origin on port 8443, with no path or credentials")
    os.umask(0o077)
    home = Path.home()
    source = Path(__file__).resolve().parent
    worker = home / "projects/f1-commentary-watchdog/ops"
    if not (worker / "agent_queue.py").exists():
        parser.error("Update the worker checkout with reviewed queue support first")
    status = command("systemctl", "--user", "show", "f1-watchdog.service", "--property=ActiveState")
    if status.split("=")[-1] in ("active", "activating", "deactivating"):
        parser.error("Let the active worker finish before installing operator code")
    destination = home / ".local/share/f1-watchdog/web"
    config = home / ".config/f1-watchdog-web"
    units = home / ".config/systemd/user"
    for path in (destination / "web", config, units, home / ".local/bin"):
        path.mkdir(parents=True, exist_ok=True)
    config.chmod(0o700)
    environment = config / "environment"
    if environment.exists() and environment.read_text().strip() != f"F1_WEB_ORIGIN={args.origin}":
        parser.error("Existing origin differs; review routing and certificate before changing it")
    for name in ("agent_queue.py", "watchdog_console.py", "watchdog_web.py", "run_recovery.py"):
        shutil.copyfile(source / name, destination / name)
        (destination / name).chmod(0o600)
    for asset in (source / "web").iterdir():
        if asset.is_file():
            shutil.copyfile(asset, destination / "web" / asset.name)
            (destination / "web" / asset.name).chmod(0o600)
    if not (config / "cert.pem").exists() and not (config / "key.pem").exists():
        try:
            ipaddress.ip_address(url.hostname)
            san = f"IP:{url.hostname}"
        except ValueError:
            san = f"DNS:{url.hostname}"
        command("openssl", "req", "-x509", "-newkey", "rsa:3072", "-nodes", "-days", "3650",
                "-keyout", str(config / "key.pem"), "-out", str(config / "cert.pem"),
                "-subj", "/CN=F1 Private Control Room", "-addext", f"subjectAltName={san}")
    if not (config / "cert.pem").exists() or not (config / "key.pem").exists():
        parser.error("Certificate/key incomplete; restore the reviewed pair")
    (config / "key.pem").chmod(0o600)
    environment.write_text(f"F1_WEB_ORIGIN={args.origin}\n")
    shutil.copyfile(source / "f1-watchdog-web.service", units / "f1-watchdog-web.service")
    launcher = home / ".local/bin/f1-web-access"
    launcher.write_text(
        '#!/bin/sh\nset -eu\nprintf "%s\\n" "Open the private control room: '
        + args.origin + '/"\nexec "$HOME/.local/share/f1-watchdog/venv/bin/python3" '
        '"$HOME/.local/share/f1-watchdog/web/watchdog_web.py" --setup-code\n')
    launcher.chmod(0o700)
    command("systemctl", "--user", "daemon-reload")
    command("systemctl", "--user", "enable", "--now", "f1-watchdog-web.service")
    command("systemctl", "--user", "restart", "f1-watchdog-web.service")
    print(f"Installed: {args.origin}/")
    print("Route LAN port 8443 to the container's 127.0.0.1:8443 using its proxy device.")
    print("In the existing authenticated browser terminal run f1-web-access for first login.")
    print(command("openssl", "x509", "-in", str(config / "cert.pem"),
                  "-noout", "-fingerprint", "-sha256"))


if __name__ == "__main__":
    main()
