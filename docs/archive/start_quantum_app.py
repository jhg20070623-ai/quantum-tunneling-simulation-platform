from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


PROJECT = Path(r"C:\Users\jiang\quantum-tunneling-sim")
LOG = Path.cwd() / "work" / "quantum_app_dev_server.log"
PID_FILE = Path.cwd() / "work" / "quantum_app_dev_server.pid"


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def fetch_title(url: str) -> tuple[int | None, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CodexLocalCheck/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            body = resp.read(200_000).decode("utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
            title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
            return resp.status, title
    except Exception as exc:
        return None, repr(exc)


def main() -> int:
    if not PROJECT.exists():
        print(f"project_missing={PROJECT}")
        return 2

    url = "http://127.0.0.1:5173/"
    if port_open(5173):
        status, title = fetch_title(url)
        print(f"already_running_url={url}")
        print(f"status={status}")
        print(f"title={title}")
        return 0

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        print("npm_missing=true")
        return 3

    LOG.parent.mkdir(parents=True, exist_ok=True)
    log_fh = LOG.open("ab")
    env = os.environ.copy()
    env["BROWSER"] = "none"
    env["NO_COLOR"] = "1"

    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        [npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort"],
        cwd=str(PROJECT),
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        env=env,
        creationflags=creationflags,
    )
    PID_FILE.write_text(str(proc.pid), encoding="ascii")

    for _ in range(60):
        if port_open(5173):
            status, title = fetch_title(url)
            print(f"started_url={url}")
            print(f"pid={proc.pid}")
            print(f"status={status}")
            print(f"title={title}")
            print(f"log={LOG}")
            return 0
        if proc.poll() is not None:
            break
        time.sleep(0.5)

    print(f"start_failed_or_timeout_pid={proc.pid}")
    print(f"log={LOG}")
    try:
        print(LOG.read_text(encoding="utf-8", errors="ignore")[-3000:])
    except Exception:
        pass
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
