from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass


@dataclass
class Listener:
    address: str
    port: int
    pid: int
    name: str = ""
    command: str = ""
    status: str = ""
    title: str = ""
    snippet: str = ""


def parse_netstat() -> list[Listener]:
    output = subprocess.check_output(["netstat", "-ano", "-p", "tcp"], text=True, encoding="mbcs", errors="replace")
    listeners: list[Listener] = []
    for line in output.splitlines():
        if "LISTENING" not in line:
            continue
        parts = line.split()
        if len(parts) < 5 or parts[0] != "TCP":
            continue
        local = parts[1]
        pid_text = parts[-1]
        if local.startswith("["):
            match = re.match(r"\[(.*)\]:(\d+)$", local)
            if not match:
                continue
            address, port_text = match.groups()
        else:
            address, port_text = local.rsplit(":", 1)
        try:
            port = int(port_text)
            pid = int(pid_text)
        except ValueError:
            continue
        if address not in {"127.0.0.1", "0.0.0.0", "::", "::1"}:
            continue
        if port < 1024 and port not in {80, 443}:
            continue
        listeners.append(Listener(address=address, port=port, pid=pid))
    return listeners


def process_map() -> dict[int, tuple[str, str]]:
    command = (
        "Get-CimInstance Win32_Process | "
        "Select-Object ProcessId,Name,CommandLine | "
        "ConvertTo-Csv -NoTypeInformation"
    )
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    mapping: dict[int, tuple[str, str]] = {}
    for row in csv.DictReader(proc.stdout.splitlines()):
        try:
            pid = int(row.get("ProcessId") or "0")
        except ValueError:
            continue
        mapping[pid] = (row.get("Name") or "", row.get("CommandLine") or "")
    return mapping


def fetch_probe(port: int) -> tuple[str, str, str]:
    url = f"http://127.0.0.1:{port}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Codex-local-probe"})
    try:
        with urllib.request.urlopen(req, timeout=0.8) as response:
            raw = response.read(12000)
            content_type = response.headers.get("content-type", "")
            text = raw.decode("utf-8", errors="replace")
            title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
            title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
            body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.I | re.S)
            body = re.sub(r"<[^>]+>", " ", body)
            body = re.sub(r"\s+", " ", body).strip()
            return f"HTTP {response.status} {content_type}", title, body[:240]
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeError) as exc:
        return type(exc).__name__, "", ""


def main() -> int:
    listeners = parse_netstat()
    procs = process_map()
    seen: dict[int, Listener] = {}
    for listener in listeners:
        key = listener.port
        if key in seen:
            continue
        listener.name, listener.command = procs.get(listener.pid, ("", ""))
        if listener.port in {135, 445, 5040, 49664, 49665, 49666, 49667, 49668, 49679}:
            continue
        listener.status, listener.title, listener.snippet = fetch_probe(listener.port)
        seen[key] = listener

    candidates = sorted(seen.values(), key=lambda item: item.port)
    print(json.dumps([asdict(item) for item in candidates], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
