from __future__ import annotations

import os
from pathlib import Path


ROOTS = [
    Path(r"D:\CDriveArchive\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件"),
    Path(r"D:\CDriveArchive\Desktop-contest"),
]
EXCLUDE_DIRS = {"node_modules", "dist", "build", ".next", ".git", "__pycache__", ".venv"}
INTERESTING_NAMES = {
    "package.json",
    "vite.config.ts",
    "vite.config.js",
    "index.html",
    "App.tsx",
    "App.jsx",
    "App.ts",
    "App.js",
}
KEYWORDS = ("量子", "隧穿", "quantum", "tunnel", "tunneling")


def should_skip(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return any(name.lower() in parts for name in EXCLUDE_DIRS)


def main() -> int:
    seen: set[Path] = set()
    results: list[Path] = []
    for root in ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dir_path = Path(dirpath)
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not should_skip(dir_path / d)]
            for filename in filenames:
                p = dir_path / filename
                if should_skip(p):
                    continue
                lower_name = filename.lower()
                full_lower = str(p).lower()
                if filename in INTERESTING_NAMES or any(k.lower() in lower_name or k.lower() in full_lower for k in KEYWORDS):
                    if p not in seen:
                        seen.add(p)
                        results.append(p)

    for p in sorted(results, key=lambda x: str(x).lower()):
        try:
            size = p.stat().st_size
        except OSError:
            size = -1
        print(f"{p}\t{size}")
    print(f"TOTAL\t{len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
