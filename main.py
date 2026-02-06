from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.config import Config

from src.backend.api import projects, upload, oauth, model_inference, pages, tasks

CURRENT_DIR = Path(__file__).resolve().parent
STATIC_DIR = CURRENT_DIR / "src/static"

app = FastAPI()

config = Config(".env")

app.add_middleware(
    SessionMiddleware,
    secret_key=config("SECRET_KEY")
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(upload.router)
app.include_router(oauth.router)
app.include_router(model_inference.router)
app.include_router(projects.router)
app.include_router(pages.router)
app.include_router(tasks.router)