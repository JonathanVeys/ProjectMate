import datetime
from typing import Dict, Any, cast
import os

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi.templating import Jinja2Templates

from .supabase_client import supabase  


router = APIRouter()
templates = Jinja2Templates(directory="src/projectMate/templates")

config = Config(".env")
oauth: OAuth = OAuth(config)

oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# LOGIN PAGE (shows "Login with Google")
@router.get("/", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# START OAUTH LOGIN
@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    print("REDIRECT URI:", redirect_uri)  # DEBUG: MUST MATCH GOOGLE CONSOLE
    return await oauth.google.authorize_redirect(request, redirect_uri) #type:ignore


# OAUTH CALLBACK
@router.get("/auth")
async def auth(request: Request):
    user_row: Dict[str, Any]
    token = await oauth.google.authorize_access_token(request) #type:ignore
    user_info = token["userinfo"]

    email = user_info["email"]
    name = user_info.get("name", "")
    avatar_url = user_info.get("picture", "")



    response = supabase.table("profiles").select("*").eq("email", email).execute()
    user_data = response.data

    if not user_data:
        insert_res = supabase.table("profiles").insert({
            "email": email,
            "name": name,
            "picture_url": avatar_url,
            "date_created": str(datetime.datetime.now())
        }).execute()

        user_row = cast(Dict[str, Any], insert_res.data[0])
    else:
        user_row = cast(Dict[str, Any], user_data[0])
    
    request.session["user"] = {
        "id": user_row["id"],             
        "email": user_row["email"],
        "name": user_row["name"],
        "picture_url": user_row["picture_url"]
    }

    return RedirectResponse(url="/pages/landing")


#Oauth logout
@router.get("/logout")
async def logout(request:Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)