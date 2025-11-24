from fastapi import APIRouter, UploadFile, File
from dotenv import load_dotenv
from openai import OpenAI
import os
import pdfplumber
import io
import json, json5, re
from datetime import datetime

load_dotenv()
router = APIRouter(prefix="/inference", tags=["inference"])


def build_model_prompt(project_spec:str) -> str:
    '''
    
    '''
    model_prompt = f'''
        Todays date = {datetime.now()}
        Make sure the answer is clean, structured, and readable. Do not omit any key detail and do not infer key facts that are not present.

        Extract all the key information from the following project specifications. Refult VALID JSON and ONLY JSON. Do not include bullet points, prose, or commentary. Make sure the answer is clean, structured, and readable. Do not omit any key detail and do not infer key facts that are not present. Follow the structure below Attribute: Value.

        deadline: The project deadline
        weighting: percentage of course grade
        description_short: A short description of the project, max 4,5 sentences.
        project_plan: A breakdown of steps needed to take to complete the project, each step should be small and managable, each step should include a rough estimation of how long it will take to complete once started in hours and a date to complete it by, based on the current date and the project deadline.
        extra: Include any adittional key information about the project like github URL, extension policies, late penalty. You may infer what the attribute name should be for each extra.

        Text to analyse:
        {project_spec}
        '''
    return model_prompt

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

def inference(file_bytes: bytes):
    '''
    Function for running model inference to generate project spec
    '''
    raw_text = extract_text_from_pdf(file_bytes)
    model_prompt = build_model_prompt(raw_text)

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )

    model_summary_raw = client.chat.completions.create(
        model="MiniMaxAI/MiniMax-M2:novita",
        messages=[
            {
                "role": "user",
                "content": model_prompt
            }
        ]
    )
    model_summary_raw = str(model_summary_raw.choices[0].message.content)
    data = parse_llm_json(model_summary_raw)

    return data

@router.post("/summarise")
async def summarise(spec_file: UploadFile = File(...)):
    '''
    API endpoint to perform model inference
    '''
    file_bytes = await spec_file.read()
    project_summary = inference(file_bytes)
    return project_summary

