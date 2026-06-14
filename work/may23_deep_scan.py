from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path.cwd()
OUT = ROOT / "work" / "may23_deep_scan_results.json"

MAY23_START = datetime(2026, 5, 23, 0, 0, 0)
MAY23_END = datetime(2026, 5, 24, 0, 0, 0)
WIDE_START = datetime(2026, 5, 20, 0, 0, 0)
WIDE_END = datetime(2026, 6, 2, 0, 0, 0)

KEYWORDS = [
    "量子",
    "隧穿",
    "虚拟仿真",
    "量子隧穿",
    "quantum",
    "tunnel",
    "tunneling",
    "schrodinger",
    "schroedinger",
    "wavefunction",
    "barrier",
]

SOURCE_NAMES = {
    "package.json",
    "vite.config.js",
    "vite.config.ts",
    "vite.config.mjs",
    "index.html",
    "tsconfig.json",
    "src",
    "dist",
    "build",
    "pnpm-lock.yaml",
    "yarn.lock",
    "package-lock.json",
}

SKIP_DIRS = {
    "$recycle.bin",
    ".git",
    ".svn",
    ".hg",
    ".cache",
    ".next",
    ".nuxt",
    ".vite",
    "node_modules",
    "__pycache__",
    "appdata\\local\\google\\chrome\\user data",
    "appdata\\local\\microsoft\\edge\\user data",
}

LIKELY_ROOTS = [
    Path(r"D:\CDriveArchive"),
    Path(r"C:\Users\jiang\Desktop"),
    Path(r"C:\Users\jiang\Documents"),
    Path(r"C:\Users\jiang\Downloads"),
]

BROWSER_HISTORY_CANDIDATES = [
    Path(r"C:\Users\jiang\AppData\Local\Google\Chrome\User Data\Default\History"),
    Path(r"C:\Users\jiang\AppData\Local\Google\Chrome\User Data\Profile 1\History"),
    Path(r"C:\Users\jiang\AppData\Local\Microsoft\Edge\User Data\Default\History"),
    Path(r"C:\Users\jiang\AppData\Local\Microsoft\Edge\User Data\Profile 1\History"),
    Path(r"C:\Users\jiang\AppData\Local\Chromium\User Data\Default\History"),
]

RECENT_CONFIGS = [
    Path(r"C:\Users\jiang\AppData\Roaming\Code\User\globalStorage\storage.json"),
    Path(r"C:\Users\jiang\AppData\Roaming\Cursor\User\globalStorage\storage.json"),
    Path(r"C:\Users\jiang\AppData\Roaming\Trae\User\globalStorage\storage.json"),
    Path(r"C:\Users\jiang\AppData\Roaming\Trae CN\User\globalStorage\storage.json"),
]


def local_dt_from_ts(ts: float) -> datetime:
    return datetime.fromtimestamp(ts).replace(microsecond=0)


def in_range(ts: float, start: datetime, end: datetime) -> bool:
    dt = local_dt_from_ts(ts)
    return start <= dt < end


def should_skip_dir(path: Path) -> bool:
    low = str(path).lower()
    name = path.name.lower()
    if name in SKIP_DIRS:
        return True
    return any(fragment in low for fragment in SKIP_DIRS if "\\" in fragment)


def text_has_keyword(text: str) -> list[str]:
    low = text.lower()
    return [kw for kw in KEYWORDS if kw.lower() in low]


def safe_read_text(path: Path, max_bytes: int = 500_000) -> str:
    try:
        with path.open("rb") as f:
            raw = f.read(max_bytes)
    except Exception:
        return ""
    for enc in ("utf-8", "utf-8-sig", "gb18030", "utf-16"):
        try:
            return raw.decode(enc, errors="ignore")
        except Exception:
            pass
    return ""


def score_project_dir(path: Path) -> dict | None:
    package_json = path / "package.json"
    if not package_json.exists():
        return None
    score = 0
    evidence: list[str] = []
    try:
        st = package_json.stat()
    except OSError:
        return None
    if in_range(st.st_mtime, WIDE_START, WIDE_END):
        score += 3
        evidence.append(f"package.json mtime {local_dt_from_ts(st.st_mtime)}")
    for name in ("vite.config.ts", "vite.config.js", "vite.config.mjs", "src", "dist", "build", "index.html"):
        if (path / name).exists():
            score += 1
            evidence.append(name)
    txt = safe_read_text(package_json)
    kws = text_has_keyword(txt)
    if kws:
        score += 5
        evidence.append("package.json keywords: " + ", ".join(kws))
    for rel in ("index.html", "src/App.tsx", "src/App.jsx", "src/App.vue", "src/main.tsx", "src/main.jsx", "src/main.js"):
        p = path / rel
        if p.exists() and p.is_file():
            ptxt = safe_read_text(p)
            kws = text_has_keyword(ptxt)
            if kws:
                score += 6
                evidence.append(f"{rel} keywords: " + ", ".join(kws))
    if score < 4:
        return None
    return {
        "path": str(path),
        "score": score,
        "evidence": evidence[:12],
        "package_mtime": str(local_dt_from_ts(st.st_mtime)),
    }


def scan_filesystem() -> dict:
    may23_hits: list[dict] = []
    project_hits: dict[str, dict] = {}
    source_file_hits: list[dict] = []

    roots = [p for p in LIKELY_ROOTS if p.exists()]
    current_work = str((ROOT / "work" / "quantum-tunneling-platform").resolve()).lower()

    for base in roots:
        for cur, dirs, files in os.walk(base):
            cur_path = Path(cur)
            cur_low = str(cur_path).lower()
            if cur_low.startswith(current_work):
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if not should_skip_dir(cur_path / d)]

            # Project directory scoring is cheap when package.json is present.
            if "package.json" in files:
                proj = score_project_dir(cur_path)
                if proj:
                    project_hits[str(cur_path)] = proj

            for name in files:
                p = cur_path / name
                low_name = name.lower()
                try:
                    st = p.stat()
                except OSError:
                    continue

                kw_in_name = text_has_keyword(str(p))
                near_may23 = in_range(st.st_mtime, WIDE_START, WIDE_END)
                exactly_may23 = in_range(st.st_mtime, MAY23_START, MAY23_END)

                if exactly_may23 and (kw_in_name or low_name in SOURCE_NAMES or low_name.endswith((".zip", ".rar", ".7z", ".mp4", ".srt", ".pptx", ".docx"))):
                    may23_hits.append(
                        {
                            "path": str(p),
                            "mtime": str(local_dt_from_ts(st.st_mtime)),
                            "size": st.st_size,
                            "keywords": kw_in_name,
                        }
                    )

                if near_may23 and low_name in {"package.json", "vite.config.ts", "vite.config.js", "index.html"}:
                    text = safe_read_text(p, max_bytes=200_000)
                    kws = text_has_keyword(text)
                    if kws or "vite" in text.lower() or "react" in text.lower():
                        source_file_hits.append(
                            {
                                "path": str(p),
                                "mtime": str(local_dt_from_ts(st.st_mtime)),
                                "size": st.st_size,
                                "keywords": kws,
                            }
                        )

    may23_hits.sort(key=lambda x: (x["mtime"], x["path"]))
    source_file_hits.sort(key=lambda x: (x["mtime"], x["path"]))
    projects = sorted(project_hits.values(), key=lambda x: (-x["score"], x["path"]))
    return {"may23_hits": may23_hits[:500], "source_file_hits": source_file_hits[:500], "project_hits": projects[:100]}


def chrome_time_to_local(microseconds: int) -> datetime:
    # Chrome/WebKit timestamp is microseconds since 1601-01-01 UTC.
    epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
    dt_utc = epoch + timedelta(microseconds=microseconds)
    return dt_utc.astimezone().replace(tzinfo=None, microsecond=0)


def query_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    tmp = Path(tempfile.gettempdir()) / f"history_{os.getpid()}_{abs(hash(str(path)))}.sqlite"
    try:
        shutil.copy2(path, tmp)
    except Exception:
        return []
    rows: list[dict] = []
    try:
        con = sqlite3.connect(str(tmp))
        cur = con.cursor()
        cur.execute(
            """
            SELECT url, title, last_visit_time, visit_count
            FROM urls
            WHERE last_visit_time > 0
            ORDER BY last_visit_time DESC
            LIMIT 200000
            """
        )
        for url, title, last_visit_time, visit_count in cur.fetchall():
            dt = chrome_time_to_local(int(last_visit_time))
            if not (datetime(2026, 5, 22) <= dt < datetime(2026, 5, 25)):
                continue
            blob = f"{url}\n{title or ''}"
            low = blob.lower()
            interested = (
                "localhost" in low
                or "127.0.0.1" in low
                or "量子" in blob
                or "隧穿" in blob
                or "tunnel" in low
                or "quantum" in low
                or url.startswith("file:")
            )
            if interested:
                safe_url = re.sub(r"([?&](?:token|code|state|access_token|id_token|refresh_token)=)[^&]+", r"\1<redacted>", url, flags=re.I)
                rows.append(
                    {
                        "browser_db": str(path),
                        "time": str(dt),
                        "url": safe_url,
                        "title": title or "",
                        "visit_count": visit_count,
                    }
                )
        con.close()
    except Exception as e:
        rows.append({"browser_db": str(path), "error": repr(e)})
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass
    rows.sort(key=lambda x: x.get("time", ""))
    return rows


def scan_browser_history() -> list[dict]:
    out: list[dict] = []
    for p in BROWSER_HISTORY_CANDIDATES:
        out.extend(query_history(p))
    return out


def scan_recent_configs() -> list[dict]:
    hits: list[dict] = []
    for p in RECENT_CONFIGS:
        if not p.exists():
            continue
        text = safe_read_text(p, max_bytes=3_000_000)
        kws = text_has_keyword(text)
        if kws or "localhost" in text.lower() or "127.0.0.1" in text.lower():
            snippets = []
            for pattern in KEYWORDS + ["localhost", "127.0.0.1"]:
                idx = text.lower().find(pattern.lower())
                if idx >= 0:
                    snippets.append(text[max(0, idx - 160) : idx + 260])
            hits.append({"path": str(p), "mtime": str(local_dt_from_ts(p.stat().st_mtime)), "keywords": kws, "snippets": snippets[:8]})
    return hits


def main() -> None:
    started = time.time()
    result = {
        "generated_at": str(datetime.now().replace(microsecond=0)),
        "filesystem": scan_filesystem(),
        "browser_history": scan_browser_history(),
        "recent_configs": scan_recent_configs(),
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Elapsed: {time.time() - started:.1f}s")
    fs = result["filesystem"]
    print(f"May23 hits: {len(fs['may23_hits'])}")
    print(f"Source file hits: {len(fs['source_file_hits'])}")
    print(f"Project hits: {len(fs['project_hits'])}")
    print(f"Browser/history hits: {len(result['browser_history'])}")
    print(f"Recent config hits: {len(result['recent_configs'])}")
    print("\nTop project hits:")
    for item in fs["project_hits"][:20]:
        print(f"[{item['score']:02d}] {item['path']} :: {'; '.join(item['evidence'][:5])}")
    print("\nBrowser/history hits:")
    for item in result["browser_history"][:80]:
        print(f"{item.get('time')} | {item.get('title')} | {item.get('url')}")


if __name__ == "__main__":
    sys.exit(main())
