import datetime
from typing import Dict, Any, cast, List

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .supabase_client import supabase

router = APIRouter(prefix="/pages", tags=["pages"])
templates = Jinja2Templates(directory="src/templates")

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
    
    res_tasks:list = supabase.table("task_progress").select("*").eq("project_id", project_id).execute().data
    res_tasks = sorted(res_tasks, key=lambda t: t["task_index"])
    if res_tasks is None:
        raise ValueError("Project has no tasks")
    completed_lookup = {t["id"]:t["completed"] for t in res_tasks}
    
    proportion_completed = round(sum(1 for t in res_tasks if t['completed']==True)/len(res_tasks)*100, 1)
    missing_tasks = [task for task in project["summary_json"]["tasks"] if not completed_lookup.get(task["id"], False)]
    remaining_effort = sum(float(task["duration"]) for task in missing_tasks)

    deadline_dt = datetime.datetime.fromisoformat(project["deadline"])
    days_remaining = (deadline_dt - datetime.datetime.now(datetime.UTC)).days

    total_number_tasks = len(res_tasks)
    
    return templates.TemplateResponse(
        "project_overview.html",
        {
            "request":request,
            "name":user["name"],
            "project_id":project_id,
            "title":project["title"],
            "description":project["description"],
            "spec_path":project["spec_path"],
            "project_spec":project["summary_json"],
            "tasks":res_tasks,
            "progress":proportion_completed,
            "days_remaining":days_remaining,
            "remaining_effort":remaining_effort,
            "total_number_tasks":total_number_tasks
        }
    )


@router.get("/tasks/{project_id}", response_class=HTMLResponse)
async def tasks_page(request:Request, project_id:str):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    
    res_project = supabase.table("projects").select("*").eq("id", project_id).execute()
    res_project = cast(Dict[str, Any], res_project.data[0])
    
    res_tasks = supabase.table("task_progress").select("*").eq("project_id", project_id).execute()
    res_tasks = cast(List[Dict[str, Any]], res_tasks.data)

    completed_lookup = {t["id"]:t["completed"] for t in res_tasks}
        
    return templates.TemplateResponse(
        "tasks.html",
        {
            "request":request,
            "project_id":project_id,
            "name":user["name"],
            "tasks":res_tasks,
            "project_summary":res_project["summary_json"],
            "completed_lookup":completed_lookup
        }
    )