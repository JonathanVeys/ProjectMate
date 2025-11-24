from fastapi import APIRouter
from .supabase_client import supabase


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/update/{task_id}")
def update_task(task_id:str, body:dict):
    completed = body.get("completed")

    supabase.table("task_progress") \
        .update({"completed": completed}) \
        .eq("id", task_id) \
        .execute()

    return {"success": True}

