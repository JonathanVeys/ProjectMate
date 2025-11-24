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
    
    res_project = supabase.table("projects").select("*").eq("id", project_id).execute()
    project = cast(Dict[str, Any], res_project.data[0])
    
    res_tasks = supabase.table("task_progress").select("*").eq("project_id", project_id).execute().data
    proportion_completed = round(sum(1 for t in res_tasks if t['completed']==True)/len(res_tasks)*100, 1)

    return templates.TemplateResponse(
        "project_overview.html",
        {
            "request":request,
            "name":user["name"],
            "title":project["title"],
            "description":project["description"],
            "spec_path":project["spec_path"],
            "project_spec":project["summary_json"],
            "tasks":res_tasks,
            "progress":proportion_completed
        }
    )