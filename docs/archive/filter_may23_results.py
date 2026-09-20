from __future__ import annotations

import json
from pathlib import Path


data = json.loads(Path("work/may23_deep_scan_results.json").read_text(encoding="utf-8"))

rows = [
    x
    for x in data.get("browser_history", [])
    if "localhost" in x.get("url", "").lower()
    or "127.0.0.1" in x.get("url", "").lower()
]

print(f"localhost_or_127_history_hits={len(rows)}")
for x in rows[:250]:
    print(f"{x.get('time')} | {x.get('title')} | {x.get('url')}")

print("\nquantum_file_history_hits")
qrows = [
    x
    for x in data.get("browser_history", [])
    if "quantum-tunneling-sim" in x.get("url", "").lower()
    or "%E9%87%8F%E5%AD%90" in x.get("url", "")
    or "%E9%9A%A7%E7%A9%BF" in x.get("url", "")
]
for x in qrows[:120]:
    print(f"{x.get('time')} | {x.get('title')} | {x.get('url')}")
