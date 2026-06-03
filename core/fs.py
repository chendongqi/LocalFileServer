import math
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException


def resolve_safe_path(root: Path, user_path: str) -> Path:
    clean = user_path.lstrip("/")
    target = (root / clean).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")
    return target


def resolve_safe_dir(root: Path, user_path: str) -> Path:
    """Like resolve_safe_path but creates intermediate dirs and doesn't require existence."""
    clean = user_path.lstrip("/")
    target = (root / clean).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    return target


def human_size(size: int) -> str:
    if size == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size, 1024)))
    i = min(i, len(units) - 1)
    val = size / (1024**i)
    return f"{val:.1f} {units[i]}" if i > 0 else f"{size} B"


def list_directory(path: Path, root: Path) -> dict:
    if not path.is_dir():
        raise HTTPException(status_code=400, detail="Not a directory")

    dirs = []
    files = []
    for item in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        try:
            stat = item.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
        except OSError:
            continue

        rel = str(item.relative_to(root))
        if item.is_dir():
            dirs.append({"name": item.name, "path": rel, "mtime": mtime})
        else:
            size = stat.st_size
            files.append({
                "name": item.name,
                "path": rel,
                "size": size,
                "size_human": human_size(size),
                "mtime": mtime,
            })

    rel_path = str(path.relative_to(root)) if path != root else ""
    parent = str(path.parent.relative_to(root)) if path != root else None

    return {
        "path": rel_path,
        "parent": parent,
        "dirs": dirs,
        "files": files,
    }
