from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.auth import require_auth

router = APIRouter(dependencies=[Depends(require_auth)])

_templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_ui(request: Request, full_path: str = ""):
    return templates.TemplateResponse(request=request, name="index.html")
