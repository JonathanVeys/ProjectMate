from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from . import upload, oauth

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="a-very-secret-key",  # change this in production
)

templates = Jinja2Templates(directory="src/projectMate/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.head("/")
async def health_check():
    return {"status": "ok"}

app.include_router(upload.router)
app.include_router(oauth.router)
