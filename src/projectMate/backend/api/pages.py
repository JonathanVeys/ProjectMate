from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="src/projectMate/templates")

@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        "landing.html",
        {"request": request, "name": user["name"]}
    )
