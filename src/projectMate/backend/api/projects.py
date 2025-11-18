from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from .supabase_client import supabase
from ...logging import logger

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/create")
async def create_project(request: Request):
    user = request.session.get("user")

    logger.info(f"[CREATE PROJECT] User session={user}")

    if not user:
        logger.warning("[CREATE PROJECT] Unauthorized access attempt")
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    title = body.get("title")
    description = body.get("description", "")

    if not title:
        return JSONResponse({"error": "Title is required"}, status_code=400)

    user_id = user["id"]  # Supabase UUID from session

    res = supabase.table("projects").insert({
        "user_id": user_id,
        "title": title,
        "description": description
    }).execute()

    logger.info(f"[CREATE PROJECT] Project created: {res.data}")

    return {"success": True, "project": res.data[0]}


@router.delete("/delete/{project_id}")
async def delete_project(request: Request, project_id:str):
    user = request.session.get("user")

    if not user:
        return JSONResponse({"error":"Not authenticated"}, status_code=401)
    user_id = user["id"]

    res = supabase.table("projects").delete().eq("id",project_id).eq("user_id", user_id).execute()
    logger.info(f"[DELETE PROJECT] Project deleted: {res.data}")

    if res.data == []:  # nothing was deleted
        return JSONResponse({"error": "Project not found or not yours"}, status_code=404)

    return {"success": True, "deleted_project": res.data}

   