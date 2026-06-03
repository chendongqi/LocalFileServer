import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

sys.path.insert(0, str(Path(__file__).parent))

from config import get_settings
from routes.files import router as files_router
from routes.ui import router as ui_router

settings = get_settings()

app = FastAPI(title="Local File Server", docs_url=None, redoc_url=None)

app.include_router(files_router)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "root": str(settings.root_dir)})


app.include_router(ui_router)


if __name__ == "__main__":
    print(f"  服务根目录: {settings.root_dir}")
    print(f"  监听地址:   http://{settings.host}:{settings.port}")
    print(f"  认证状态:   {'已启用' if settings.auth_enabled else '未启用'}")
    print(f"  允许删除:   {'是' if settings.allow_delete else '否'}")
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
