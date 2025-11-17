from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pdfplumber
import io
import docx

from src.projectMate.logging import logger


router = APIRouter(prefix="/upload", tags=["upload"])
templates = Jinja2Templates(directory="src/projectMate/templates")

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



@router.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/")  # force login

    return templates.TemplateResponse("landing.html", {"request": request, "name": user["name"]})