from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path


HOME = Path.home()
WORKSPACE = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026")
KEYWORDS = ("量子隧穿", "隧穿", "quantum tunneling", "quantum-tunneling", "tunnel")
EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    ".cache",
    "__pycache__",
    "AppData",
    "$Recycle.Bin",
    "System Volume Information",
}


def query_browser_history() -> list[dict]:
    history_paths = [
        HOME / r"AppData\Local\Google\Chrome\User Data\Default\History",
        HOME / r"AppData\Local\Google\Chrome\User Data\Profile 1\History",
        HOME / r"AppData\Local\Microsoft\Edge\User Data\Default\History",
        HOME / r"AppData\Local\Microsoft\Edge\User Data\Profile 1\History",
    ]
    rows: list[dict] = []
    for history in history_paths:
        if not history.exists():
            continue
        tmp = Path(tempfile.gettempdir()) / f"history-{history.parent.name}-{history.name}.sqlite"
        try:
            shutil.copy2(history, tmp)
            conn = sqlite3.connect(tmp)
            cur = conn.cursor()
            cur.execute(
                """
                SELECT url, title, last_visit_time
                FROM urls
                WHERE url LIKE '%localhost%'
                   OR url LIKE '%127.0.0.1%'
                   OR title LIKE '%量子%'
                   OR title LIKE '%隧穿%'
                   OR title LIKE '%quantum%'
                   OR title LIKE '%tunnel%'
                ORDER BY last_visit_time DESC
                LIMIT 80
                """
            )
            for url, title, last_visit_time in cur.fetchall():
                rows.append(
                    {
                        "source": str(history),
                        "url": url,
                        "title": title,
                        "last_visit_time": last_visit_time,
                    }
                )
            conn.close()
        except Exception as exc:
            rows.append({"source": str(history), "error": str(exc)})
        finally:
            try:
                tmp.unlink()
            except OSError:
                pass
    return rows


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)


def text_file_candidate(path: Path) -> bool:
    return path.suffix.lower() in {
        ".json",
        ".html",
        ".htm",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".css",
        ".md",
        ".txt",
        ".vue",
    }


def search_files() -> list[dict]:
    roots = [
        Path(r"D:\CDriveArchive"),
        HOME / "Desktop",
        HOME / "Documents",
        HOME / "Downloads",
    ]
    results: list[dict] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            current = Path(dirpath)
            if should_skip(current):
                dirnames[:] = []
                continue
            dirnames[:] = [name for name in dirnames if name not in EXCLUDE_DIRS]
            for filename in filenames:
                path = current / filename
                if path in seen or should_skip(path):
                    continue
                seen.add(path)
                path_text = str(path).lower()
                name_hit = any(keyword.lower() in path_text for keyword in KEYWORDS)
                package_like = filename in {"package.json", "vite.config.ts", "vite.config.js", "index.html"}
                content_hit = False
                if (name_hit or package_like or text_file_candidate(path)) and path.exists():
                    try:
                        if path.stat().st_size <= 2_000_000 and text_file_candidate(path):
                            text = path.read_text(encoding="utf-8", errors="ignore").lower()
                            content_hit = any(keyword.lower() in text for keyword in KEYWORDS)
                    except OSError:
                        pass
                if name_hit or content_hit:
                    results.append(
                        {
                            "path": str(path),
                            "size": path.stat().st_size if path.exists() else None,
                            "name_hit": name_hit,
                            "content_hit": content_hit,
                            "is_workspace_generated": str(path).startswith(str(WORKSPACE / "work" / "quantum-tunneling-platform")),
                        }
                    )
    return results[:300]


def main() -> int:
    output = {
        "history": query_browser_history(),
        "files": search_files(),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
