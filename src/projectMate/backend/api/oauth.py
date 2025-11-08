from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="src/projectMate/templates")

config = Config(".env")
oauth = OAuth(config)

oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/")
async def login(request: Request):
    redirect_uri = request.url_for("auth")  # callback
    return await oauth.google.authorize_redirect(request, redirect_uri) #type:ignore

@router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request) #type:ignore
    user_info = token["userinfo"]

    # 🔐 Store the user in session
    request.session["user"] = user_info

    # Redirect to upload page after login
    return RedirectResponse(url="/upload/")
