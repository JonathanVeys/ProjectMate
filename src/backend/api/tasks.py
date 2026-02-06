from fastapi import APIRouter
from pydantic import BaseModel

from .supabase_client import supabase
from ...logging import logger


router = APIRouter(prefix="/tasks", tags=["tasks"])


class Task(BaseModel):
    project_id: str
    description: str
    duration: int | None = None
    due_date: str | None = None
    task_index: int
    completed: bool = False



@router.patch("/update/{task_id}")
def updateTask(task_id:str, body:dict):
    '''
    API endpoint for updating the status of a task from uncompleted to completed
    
    :param task_id: The ID of the task that needs updating
    :type task_id: str
    :param body: The new body of the task
    :type body: dict
    '''
    completed = body.get("completed")

    supabase.table("task_progress") \
        .update({"completed": completed}) \
        .eq("id", task_id) \
        .execute()

    return {"success": True}


def insertTask(projectId:str, body: dict, taskIdx:int|None=None):
    body["project_id"] = projectId
    if taskIdx is not None:
        body["task_index"] = taskIdx
    supabase.table("task_progress").insert(body).execute()

@router.post("/create/{project_id}") 
def createTask(projectId:str, task:Task, taskIdx:int|None=None):
    '''
    API enpoint for creating a new task for a project
    
    :param project_id: The ID for the project that the task is assigned to
    :type project_id: str
    :param task: A task object containing all the information about the task
    :type task: Task
    '''
    try:
        data = task.model_dump()
        insertTask(projectId, data, taskIdx)
        return {"success": True}
    except Exception as e:
        logger.exception("Failed to create task")
        return {"success": False, "error": str(e)}