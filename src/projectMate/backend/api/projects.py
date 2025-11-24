from typing import Dict, Any, cast

from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import JSONResponse

from .supabase_client import supabase
from .model_inference import inference
from ...logging import logger

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/create")
async def create_project(
    request: Request,
    title: str = Form(...),
    deadline: str = Form(...),
    description: str = Form(...),
    spec_file: UploadFile = File(None)
):
    '''
    API endpoint for creating a new project
    '''
    user = request.session.get("user")
    if not user:
        return {"success": False, "error": "Not authenticated"}
    
    contents = await spec_file.read()
    project_summary = cast(Dict[str, Any], inference(contents))

    # 1. Insert the project first
    res = supabase.table("projects").insert({
        "user_id": user['id'],
        "title": title,
        "deadline": deadline,
        "description": description,
        "summary_json":project_summary
    }).execute()

    logger.info("[CREATE PROJECT] Model Inference")
    project = cast(Dict[str,Any], res.data[0])
    project_id = project["id"]

    # 2. If file uploaded, save it in a folder named after project_id
    if spec_file:
        filename = spec_file.filename
        file_path = f"{project_id}/{filename}"

        supabase.storage.from_("project_spec").upload(
            file_path,
            contents,
            {
                "content-type": "application/pdf"
            }
        )

        # 3. Optionally store file URL/path in the DB
        supabase.table("projects").update({
            "spec_path": file_path
        }).eq("id", project_id).execute()

    for i, task in enumerate(project_summary['project_plan']):
        supabase.table("task_progress").insert({
            "project_id": project_id,
            "task_index": i,
            "completed": False
        }).execute()

    return {"success": True}


@router.delete("/delete/{project_id}")
async def delete_project(request: Request, project_id:str):
    '''
    API endpoint for deleting a project
    '''
    user = request.session.get("user")

    if not user:
        return JSONResponse({"error":"Not authenticated"}, status_code=401)
    user_id = user["id"]

    #Remove row relating to project
    res = supabase.table("projects").delete().eq("id",project_id).eq("user_id", user_id).execute()
    logger.info(f"[DELETE PROJECT] Project deleted: {res.data}")

    #Remove files relating to project
    files = supabase.storage.from_("project_spec").list(project_id)
    file_paths = [f"{project_id}/{file['name']}" for file in files]
    supabase.storage.from_("project_spec").remove(file_paths)
    logger.info(f"[DELETE PROJECT] Project Files Deleted {project_id}")


    if res.data == []:  # nothing was deleted
        return JSONResponse({"error": "Project not found or not yours"}, status_code=404)

    return {"success": True, "deleted_project": res.data}

   