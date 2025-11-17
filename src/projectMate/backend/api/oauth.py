# from fastapi import APIRouter, Request
# from fastapi.responses import RedirectResponse, HTMLResponse
# from authlib.integrations.starlette_client import OAuth
# from starlette.config import Config

# router = APIRouter(tags=["auth"])

# config = Config(".env")
# oauth = OAuth(config)

# oauth.register(
#     name="google",
#     client_id=config("GOOGLE_CLIENT_ID"),
#     client_secret=config("GOOGLE_CLIENT_SECRET"),
#     server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
#     client_kwargs={"scope": "openid email profile"},
# )


# @router.get("/login")
# async def login(request: Request):
#     redirect_uri = request.url_for("auth")  # callback
#     print("Redirect URI:", redirect_uri)
#     return await oauth.google.authorize_redirect(request, redirect_uri) #type:ignore


# @router.get("/auth")
# async def auth(request: Request):
#     token = await oauth.google.authorize_access_token(request) #type:ignore
#     user_info = token["userinfo"]

#     # 🔐 Store the user in session
#     request.session["user"] = user_info

#     # Redirect to upload page after login
#     return RedirectResponse(url="/")



from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi.templating import Jinja2Templates

router = APIRouter()
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


# -----------------------------------------
# LOGIN PAGE (shows "Login with Google")
# -----------------------------------------
@router.get("/", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# -----------------------------------------
# START OAUTH LOGIN
# -----------------------------------------
@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    print("REDIRECT URI:", redirect_uri)  # DEBUG: MUST MATCH GOOGLE CONSOLE
    return await oauth.google.authorize_redirect(request, redirect_uri)


# -----------------------------------------
# OAUTH CALLBACK
# -----------------------------------------
@router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    # Save user in session
    request.session["user"] = user_info

    # Redirect to landing page
    return RedirectResponse(url="/landing")


# -----------------------------------------
# LANDING PAGE (requires login)
# -----------------------------------------
@router.get("/landing", response_class=HTMLResponse)
async def landing_page(request: Request):
    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/")  # back to login

    return templates.TemplateResponse(
        "landing.html",
        {"request": request, "name": user["name"]}
    )
