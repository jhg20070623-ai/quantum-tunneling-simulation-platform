from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


ROOTS = [
    Path(r"D:\CDriveArchive"),
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Downloads",
]

START = datetime(2026, 5, 22, 0, 0, 0)
END = datetime(2026, 5, 24, 23, 59, 59)

EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    ".cache",
    "__pycache__",
    ".venv",
    "AppData",
    "$Recycle.Bin",
    "System Volume Information",
}

PROJECT_MARKERS = {
    "package.json",
    "vite.config.ts",
    "vite.config.js",
    "index.html",
    "src",
    "App.tsx",
    "App.jsx",
    "App.ts",
    "App.js",
}

KEYWORDS = ("量子", "隧穿", "quantum", "tunnel", "tunneling")


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def stat_time(path: Path) -> datetime | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return None


def in_window(path: Path) -> bool:
    t = stat_time(path)
    return bool(t and START <= t <= END)


def score_path(path: Path) -> int:
    text = str(path).lower()
    name = path.name
    score = 0
    if any(k.lower() in text for k in KEYWORDS):
        score += 50
    if name in PROJECT_MARKERS:
        score += 30
    if path.suffix.lower() in {".zip", ".7z", ".rar"}:
        score += 15
    if "vite" in text or "react" in text or "src" in path.parts:
        score += 10
    if in_window(path):
        score += 20
    return score


def collect() -> dict:
    exact_day = []
    project_dirs: dict[str, dict] = {}
    archives = []

    for root in ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            current = Path(dirpath)
            if is_excluded(current):
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

            if in_window(current):
                exact_day.append(record(current, "dir"))

            marker_names = set(filenames) | set(dirnames)
            if marker_names & PROJECT_MARKERS:
                score = score_path(current) + sum(10 for marker in marker_names if marker in PROJECT_MARKERS)
                if score >= 30 or any(in_window(current / m) for m in marker_names if (current / m).exists()):
                    project_dirs[str(current)] = {
                        "path": str(current),
                        "mtime": fmt_time(current),
                        "score": score,
                        "markers": sorted(marker_names & PROJECT_MARKERS),
                    }

            for filename in filenames:
                path = current / filename
                if is_excluded(path):
                    continue
                s = score_path(path)
                if in_window(path) or s >= 50:
                    rec = record(path, "file")
                    rec["score"] = s
                    exact_day.append(rec)
                if path.suffix.lower() in {".zip", ".7z", ".rar"} and (in_window(path) or s >= 30):
                    archives.append(record(path, "archive"))

    exact_day_sorted = sorted(exact_day, key=lambda item: (-item.get("score", 0), item["path"]))[:500]
    project_sorted = sorted(project_dirs.values(), key=lambda item: (-item["score"], item["path"]))[:120]
    archive_sorted = sorted(archives, key=lambda item: item["path"])[:120]
    return {
        "window": f"{START:%Y-%m-%d %H:%M} to {END:%Y-%m-%d %H:%M}",
        "project_dirs": project_sorted,
        "archives": archive_sorted,
        "exact_day_files_and_dirs": exact_day_sorted,
    }


def record(path: Path, kind: str) -> dict:
    try:
        size = path.stat().st_size if path.is_file() else None
    except OSError:
        size = None
    return {
        "kind": kind,
        "path": str(path),
        "mtime": fmt_time(path),
        "size": size,
    }


def fmt_time(path: Path) -> str:
    t = stat_time(path)
    return t.strftime("%Y-%m-%d %H:%M:%S") if t else ""


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
