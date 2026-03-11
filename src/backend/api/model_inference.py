from fastapi import APIRouter, UploadFile, File
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber
import io
import json, json5, re
from datetime import datetime
from typing import cast, Dict, Any, List

from .supabase_client import supabase

load_dotenv()
router = APIRouter(prefix="/inference", tags=["inference"])

def extract_text_from_pdf(file_bytes: bytes) -> str:
    '''
    '''
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
    
def parse_llm_json(raw: str):
    # Step 1 — Try strict JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Step 2 — Extract JSON substring
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    
    json_str = match.group(0)

    # Step 3 — Try strict again
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Step 4 — fallback: tolerant parser
    return json5.loads(json_str)

def normalize_deadline(value):
    """Convert string or datetime deadline into YYYY-MM-DD format safely."""
    if isinstance(value, str):
        try:
            # Convert ISO string to datetime
            dt = datetime.fromisoformat(value.replace("Z", ""))
            return dt.strftime("%Y-%m-%d")
        except:
            return value  # fallback if parse fails
    elif hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return None

def calculate_days_remaining(deadline_str: str) -> int:
    dt = datetime.fromisoformat(deadline_str.replace("Z", ""))
    now = datetime.now(dt.tzinfo)
    return (dt.date() - now.date()).days


def build_summary_prompt(project_spec: str, deadline:str|None=None) -> str:
    model_prompt = f"""
    Todays date: {datetime.now()}
    Deadline: {deadline}

    You are a project information extraction assistant. 
    Your job is to read the following project specification and extract ALL key information, without adding or inferring anything that is not explicitly present in the text.

    ⚠ IMPORTANT RULES:
    - Return **VALID JSON ONLY**.
    - Do NOT include explanations, commentary, or bullet points outside JSON.
    - If a field is not mentioned in the text, return null.
    - Do NOT infer weighting, deliverables, deadlines, or policies.
    - Every task must directly originate from the project spec text.
    - All dates must be ISO format if present, otherwise null.
    - Each task should be short and precise, aim for tasks that should not take longer then 1-2 hours at a time.
    - If deadline provided is a valid date, then assume that is the true deadline for the project regardless of what the spec says

    THE JSON SCHEMA YOU MUST RETURN:

    {{
    "deadline": string or null,
    "weighting": string or null,
    "description_short": string,
    "description_long": string or null,
    "deliverables": [
        {{ "name": string, "details": string or null }}
    ],
    "datasets": [
        {{ "name": string, "details": string or null }}
    ],
    "methods_required": [
        string
    ],
    "evaluation_metrics": [
        string
    ],
    "submission_requirements": [
        string
    ],
    "tasks": [
        {{
            "task" (str): Title of task,
            "description" (str): A description detailing what exactly must be done for this task. 2-3 Sentences long,
            "duration" (int): The time in hours that it should take to complete the task, only as a interger or float, no characters,
            "due_date" (iso): The date that the user should complete this task to stay on track
        }}
    ],
    "extra": {{
        "late_policy": string or null,
        "extension_policy": string or null,
        "github_url": string or null,
        "other_notes": string or null

    }}
    }}

    Instructions for fields:

    - "description_short": 3–5 sentence summary of the project.
    - "deliverables": items the student must submit.
    - "methods_required": models, algorithms, or approaches the spec requires.
    - "tasks": actionable steps required to complete the project.
    - A task should represent a coherent 1–2 hour block of work a student would naturally complete in one sitting.
    - Merge multiple related instructions into a single task if they clearly describe the same work item.
    - Do NOT generate a separate task for every sentence.
    - Avoid duplicate tasks (e.g., “implement Dropout” and “write fprop/bprop” should be one combined task).
    - Aim for roughly 8–15 tasks total unless the project specification is unusually long.
    - Each task must cite at least one source sentence from the text. If multiple sentences feed into a task, pick the most representative one.
    - Each task should include a date to complete the task by to keep the user on track, aim for the last task to be completed a 2 days before the deadline.
    - "submission_requirements": formatting, report length, file types, etc.
    - "extra": anything important but uncategorised.

    Now extract the information from the project specification below.

    TEXT TO ANALYSE:
    \"\"\"{project_spec}\"\"\"
    """
    return model_prompt

def build_next_tasks_prompt(state:dict) -> str:
    return f"""
        Today's date: {state["today"]}

        You are a project planning assistant. 
        Generate 3–5 recommended tasks that the user should do next. Each task should not take more then 1-2 hours to complete and should aim to be precise.

        Use the information below:

        PROJECT TITLE:
        {state["title"]}

        DEADLINE:
        {state["deadline"]} (in {state["days_remaining"]} days)

        SHORT DESCRIPTION:
        {state["description"]}

        TASKS COMPLETED:
        {state["tasks_completed"]}

        TASKS STILL NOT DONE:
        {state["tasks_incomplete"]}

        ESTIMATED HOURS REMAINING:
        {state["estimated_hours_remaining"]}

        INSTRUCTIONS:
        - Recommend only tasks that exist in the project specification.
        - Return a list of 3–5 tasks in JSON format.
        - For each task, include:
            - "task": name of the task
            - "reason": why it's recommended
            - "estimated_time_hours": your best estimate
            - "urgency": "low", "medium", or "high"
        - Consider dependency order (e.g., cannot write results before running experiments).
        - If writing tasks remain and the deadline is near, prioritise writing.
        - If experiments remain, prioritise experiments before analysis.

        Return ONLY JSON.

        """

    



def inference(prompt: str):
    '''
    Function for running model inference to generate project spec
    '''

    client = OpenAI()

    response = client.responses.create(
    model="gpt-5-mini",
    input=prompt
    )

    return response.output_text

@router.post("/summarise")
async def summarise(spec_file: UploadFile = File(...)):
    '''
    API endpoint to perform model inference
    '''
    file_bytes = await spec_file.read()
    raw_text = extract_text_from_pdf(file_bytes)
    model_prompt = build_summary_prompt(raw_text)
    project_summary = inference(model_prompt)
    return project_summary


@router.post("/next_tasks")
async def next_steps(project_id:str):
    '''
    Docstring for next_steps
    
    :param project_id: Description
    :type project_id: str
    '''
    project_res = supabase.table("projects").select("*").eq("id", project_id).execute()
    project = cast(Dict[str, Any], project_res.data[0])

    tasks_res = supabase.table("task_progress").select("*").eq("project_id", project_id).execute()
    tasks = cast(List[Dict[str, Any]], tasks_res.data)

    completed_idx = [task["task_index"] for task in tasks if task["completed"]==True]
    completed_tasks = [task for idx,task in enumerate(project["summary_json"]["tasks"]) if idx in completed_idx]

    incompleted_idx = [task["task_index"] for task in tasks if task["completed"]==False]
    incompleted_tasks = [task for idx,task in enumerate(project["summary_json"]["tasks"]) if idx in incompleted_idx]
    tasks = tasks_res.data

    project_state = {
        "title": project["title"],
        "deadline": normalize_deadline(project["deadline"]),
        "today": datetime.now(),
        "days_remaining": calculate_days_remaining(project["deadline"]),
        "description": project["summary_json"]["description_short"],
        "tasks":tasks,
        "tasks_completed": completed_tasks,
        "tasks_incomplete": incompleted_tasks,
        "estimated_hours_remaining": []
    }

    prompt = build_next_tasks_prompt(project_state)

    next_tasks_raw = inference(prompt)
    next_tasks = parse_llm_json(next_tasks_raw)

    return next_tasks