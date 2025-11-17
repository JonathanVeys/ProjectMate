from fastapi import APIRouter
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from pydantic import BaseModel

load_dotenv()
router = APIRouter(prefix="/inference", tags=["inference"])


def build_model_prompt(project_spec:str) -> str:
    model_prompt = f'''
        Extract all key information from the following project specification. Return VALID JSON and ONLY JSON. Do not include bullet points, prose, or commentary.

        Deadline

        Weighting (percentage of the course grade)

        Short Description (2–3 sentences summarising the project)

        Deliverables (bullet list of what the student must submit)

        Project Breakdown

        Break the project into its major sections or components

        For each section, provide a concise summary of 2–4 sentences

        Important Notes

        Include information such as extension policies, group work rules, late penalties, required technologies, reporting requirements, formatting constraints, or any other emphasised details in the specification

        Text to analyse:
        {project_spec}

        Make sure the answer is clean, structured, and readable. Do not omit any key detail and do not infer key facts that are not present.
        '''
    return model_prompt

class ProjectSpecRequest(BaseModel):
    project_spec:str

@router.post("/")
def summarise(body:ProjectSpecRequest):
    '''
    
    '''
    project_spec = body.project_spec
    model_prompt = build_model_prompt(project_spec)

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )

    completion = client.chat.completions.create(
        model="MiniMaxAI/MiniMax-M2:novita",
        messages=[
            {
                "role": "user",
                "content": model_prompt
            }
        ],
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content
