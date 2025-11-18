from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.config import Config

from . import projects, upload, oauth, model_inference, pages

CURRENT_DIR = Path(__file__).resolve()
BASE_DIR = CURRENT_DIR.parent.parent.parent  # -> src/projectMate/
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"


app = FastAPI()

config = Config(".env")

app.add_middleware(
    SessionMiddleware,
    secret_key=config("SECRET_KEY")
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory="src/projectMate/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(upload.router)
app.include_router(oauth.router)
app.include_router(model_inference.router)
app.include_router(projects.router)
app.include_router(pages.router)

