from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.config import Config

from . import upload, oauth

app = FastAPI()

config = Config(".env")

app.add_middleware(
    SessionMiddleware,
    secret_key=config("SECRET_KEY")
)
app.mount("/static", StaticFiles(directory="src/projectMate/static"), name="static")

templates = Jinja2Templates(directory="src/projectMate/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.head("/")
async def health_check():
    return {"status": "ok"}

app.include_router(upload.router)
app.include_router(oauth.router)
