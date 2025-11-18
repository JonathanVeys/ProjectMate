import datetime

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .supabase_client import supabase

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="src/projectMate/templates")

@router.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    
    # Fetch all projects for this Supabase user
    res = supabase.table("projects").select("*").eq("user_id", user["id"]).execute()
    projects = res.data if res.data else []

    # Format timestamps
    for p in projects:
        if p.get("created_at"):
            dt = datetime.datetime.fromisoformat(p["created_at"].replace("Z", "+00:00"))
            p["created_at_readable"] = dt.strftime("%d-%b-%Y")  

    return templates.TemplateResponse(
        "landing.html",
        {
            "request": request, 
            "name": user["name"],
            "projects": projects
        }
    )
