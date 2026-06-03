from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File

from config import Settings, get_settings
from core.auth import require_auth
from core.fs import list_directory, resolve_safe_dir, resolve_safe_path
from core.streaming import file_stream_response

router = APIRouter(prefix="/api", dependencies=[Depends(require_auth)])


@router.get("/list")
async def list_dir(
    path: str = "",
    settings: Settings = Depends(get_settings),
):
    root = settings.root_dir
    if path:
        target = resolve_safe_path(root, path)
    else:
        target = root
    return list_directory(target, root)


@router.get("/download")
async def download_file(
    path: str,
    request: Request,
    settings: Settings = Depends(get_settings),
):
    target = resolve_safe_path(settings.root_dir, path)
    if target.is_dir():
        raise HTTPException(status_code=400, detail="Cannot download a directory")
    return await file_stream_response(target, request)


@router.post("/upload")
async def upload_file(
    path: str = "",
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    root = settings.root_dir
    if path:
        dest_dir = resolve_safe_dir(root, path)
    else:
        dest_dir = root

    if not dest_dir.is_dir():
        raise HTTPException(status_code=400, detail="Target path is not a directory")

    safe_name = Path(file.filename or "upload").name
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename")

    dest = dest_dir / safe_name

    written = 0
    async with aiofiles.open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            written += len(chunk)
            if written > settings.max_upload_size:
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large")
            await out.write(chunk)

    return {"filename": safe_name, "size": written, "path": str(dest.relative_to(root))}


@router.get("/mkdir")
async def make_dir(
    path: str,
    settings: Settings = Depends(get_settings),
):
    root = settings.root_dir
    target = resolve_safe_dir(root, path)
    if target.exists():
        raise HTTPException(status_code=409, detail="Already exists")
    target.mkdir(parents=True, exist_ok=False)
    return {"created": str(target.relative_to(root))}
