import mimetypes
import re
from pathlib import Path

import aiofiles
from fastapi import Request
from fastapi.responses import Response, StreamingResponse

CHUNK_SIZE = 1024 * 1024  # 1MB


async def file_stream_response(path: Path, request: Request) -> Response:
    file_size = path.stat().st_size
    mime_type, _ = mimetypes.guess_type(path.name)
    if mime_type is None:
        mime_type = "application/octet-stream"

    range_header = request.headers.get("Range")
    if range_header:
        match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1

            async def range_generator():
                async with aiofiles.open(path, "rb") as f:
                    await f.seek(start)
                    remaining = length
                    while remaining > 0:
                        chunk = await f.read(min(CHUNK_SIZE, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
                "Content-Disposition": f'attachment; filename="{path.name}"',
            }
            return StreamingResponse(
                range_generator(), status_code=206, media_type=mime_type, headers=headers
            )

    async def full_generator():
        async with aiofiles.open(path, "rb") as f:
            while chunk := await f.read(CHUNK_SIZE):
                yield chunk

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Disposition": f'attachment; filename="{path.name}"',
    }
    return StreamingResponse(
        full_generator(), status_code=200, media_type=mime_type, headers=headers
    )
