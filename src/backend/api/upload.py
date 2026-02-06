from fastapi import APIRouter, File, UploadFile, HTTPException, Request
import pdfplumber
import io
import docx
from dotenv import load_dotenv
from pydantic import BaseModel


from src.logging import logger


router = APIRouter(prefix="/upload", tags=["upload"])

load_dotenv()
router = APIRouter(prefix="/inference", tags=["inference"])


def build_model_prompt(project_spec:str) -> str:
    model_prompt = f'''
        Make sure the answer is clean, structured, and readable. Do not omit any key detail and do not infer key facts that are not present.

        Extract all the key information from the following project specifications. Refult VALID JSON and ONLY JSON. Do not include bullet points, prose, or commentary. Make sure the answer is clean, structured, and readable. Do not omit any key detail and do not infer key facts that are not present. Follow the structure below Attribute: Value.

        deadline: The project deadline
        weighting: percentage of course grade
        description_short: A short description of the project, max 4,5 sentences.
        project_plan: A breakdown of steps needed to take to complete the project, each step should include a rough estimation of how long it will take to complete and a date to complete it by, based on the current date and the project deadline.
        extra: Include any adittional key information about the project like github URL, extension policies, late penalty. You may infer what the attribute name should be for each extra.

        Text to analyse:
        {project_spec}
        '''
    return model_prompt

class ProjectSpecRequest(BaseModel):
    project_spec:str

def detect_file_type(file: UploadFile) -> str:
    filename = file.filename.lower() #type:ignore
    content_type = file.content_type
    if isinstance(content_type, str):
        if filename.endswith(".pdf") or content_type == "application/pdf":
            return "pdf"
        elif filename.endswith(".docx") or content_type in {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}:
            return "docx"
        elif filename.endswith(".txt") or content_type.startswith("text/"):
            return "txt"
    raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_type = detect_file_type(file)

    file_bytes = await file.read()

    if file_type == "pdf":
        text = extract_text_from_pdf(file_bytes)
    elif file_type == "docx":
        text = extract_text_from_docx(file_bytes)
    elif file_type == "txt":
        text = extract_text_from_txt(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")


    return {
        "filename": file.filename,
        "type": file_type,
        "length": len(text),
        "preview": text
    }

