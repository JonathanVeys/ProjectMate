from typing import Dict, Any, cast

from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import uuid

from .supabase_client import supabase
from .model_inference import inference, build_summary_prompt, extract_text_from_pdf, parse_llm_json
from .tasks import insertTask
from ...logging import logger

'''
API endpoint for handling projects including editing, creating and deleting them.
'''

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

    #Ensure a valid user is provided
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    #Generate project summary if spec_file is provide, else generate an empty dict for testing
    if spec_file:
        contents = await spec_file.read()
        raw_text = extract_text_from_pdf(contents)
        model_prompt = build_summary_prompt(raw_text)
        project_summary = inference(model_prompt)
        project_summary = parse_llm_json(project_summary)
        project_summary = cast(Dict[str, Any], project_summary)
        for task in project_summary["tasks"]: 
            task["id"] = str(uuid.uuid4())
    else:
        project_summary = dict()


    # 1. Insert the project first
    try:
        res = supabase.table("projects").insert({
            "user_id": user['id'],
            "title": title,
            "deadline": deadline,
            "description": description,
            "summary_json":project_summary
        }).execute()

        #Log that the project has been successfully created
        logger.info(f"[CREATE PROJECT] Project created")
        project = cast(Dict[str,Any], res.data[0])
        project_id = project["id"]
    except Exception as e:
        logger.warning(f"[CREATE PROJECT] Failed to create new project | Error: {e}")
        raise HTTPException(status_code=401, detail=f"Failed to create project: {e}")
    

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

    if "tasks" in project_summary.keys():
        for i, task in enumerate(project_summary['tasks']):   
            insertTask(projectId=project_id, taskIdx=i, body=
                    {
                        "id": task["id"],
                        "project_id": project_id,
                        "task_index": i,
                        "completed": False,
                        "description": task["task"],
                        "duration":task["duration"],
                        "due_date":task["due_date"],
                    })
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
    res = cast(Dict[str,Any], res.data[0])
    logger.info(f"[DELETE PROJECT] Project deleted: {res["id"]}")

    #Remove files relating to project
    files = supabase.storage.from_("project_spec").list(project_id)
    file_paths = [f"{project_id}/{file['name']}" for file in files]
    if file_paths:
        supabase.storage.from_("project_spec").remove(file_paths)
        logger.info(f"[DELETE PROJECT] Project Files Deleted {project_id}")


    if res == []:  # nothing was deleted
        return JSONResponse({"error": "Project not found or not yours"}, status_code=404)

    return {"success": True, "deleted_project": res["id"]}

   