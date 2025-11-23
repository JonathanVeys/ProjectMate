import datetime
from typing import Dict, Any, cast

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .supabase_client import supabase

router = APIRouter(prefix="/pages", tags=["pages"])
templates = Jinja2Templates(directory="src/projectMate/templates")

@router.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    
    # Fetch all projects for this Supabase user
    res = supabase.table("projects").select("*").eq("user_id", user["id"]).execute()
    projects = cast(list[Dict[str, Any]], res.data if res.data else [])

    # Format timestamps
    for p in projects:
        if p.get("deadline"):
            dt = datetime.datetime.fromisoformat(p["deadline"].replace("Z", "+00:00"))
            p["deadline_at_readable"] = dt.strftime("%d-%b-%Y")  

    return templates.TemplateResponse(
        "landing.html",
        {
            "request": request, 
            "name": user["name"],
            "projects": projects
        }
    )


@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_page(request: Request, project_id: str):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    
    res = supabase.table("projects").select("*").eq("id", project_id).execute()
    project = cast(Dict[str, Any], res.data[0])
    
    spec_path = project["spec_path"]  # e.g. "project-id/file.pdf"

    # Generate a signed URL (valid for 1 hour)
    signed = supabase.storage.from_("project_spec").create_signed_url(
        spec_path,
        60 * 60 
    )

    signed_url = signed.get("signedURL") or signed.get("signed_url")

    return templates.TemplateResponse(
        "project_overview.html",
        {
            "request":request,
            "name":user["name"],
            "title":project["title"],
            "description":project["description"],
            "spec_path":project["spec_path"],
            "spec_url":signed_url,
            "project_spec":project["summary_json"]
        }
    )