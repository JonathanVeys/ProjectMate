import datetime
from typing import Dict, Any, cast
import os

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi.templating import Jinja2Templates

from .supabase_client import supabase  
from ...logging import logger


router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

config = Config(".env")
oauth: OAuth = OAuth(config)

oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="github",
    client_id=config("GITHUB_CLIENT_ID"),
    client_secret=config("GITHUB_CLIENT_SECRET"),
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)


@router.get("/", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/login/google")
async def login_google(request: Request):
    assert oauth.google is not None
    redirect_uri = request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri) 

@router.get("/login/github")
async def login_github(request: Request):
    assert oauth.github is not None
    redirect_uri = request.url_for("auth_github")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/auth/google")
async def auth_google(request: Request):
    '''
    '''
    assert oauth.google is not None
    user_row: Dict[str, Any]
    token = await oauth.google.authorize_access_token(request)
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

@router.get("/auth/github")
async def auth_github(request:Request):
    '''
    Docstring for auth_github
    
    :param request: Description
    :type request: Request
    '''
    assert oauth.github is not None
    token = await oauth.github.authorize_access_token(request) 

    # Get main user object
    user_resp = await oauth.github.get("user", token=token)
    user_info = user_resp.json()

    email_resp = await oauth.github.get("user/emails", token=token)
    emails = email_resp.json()

    email = None
    for e in emails:
        if e.get("primary") and e.get("verified"):
            email = e["email"]
            break


    if email is None:
        email = user_info.get("email")

    name = user_info.get("name") or user_info.get("login")
    avatar_url = user_info.get("avatar_url", "")


    response = supabase.table("profiles").select("*").eq("email", email).execute()
    user_data = response.data

    if not user_data:
        insert_res = supabase.table("profiles").insert({
            "email": email,
            "name": name,
            "picture_url": avatar_url,
            "date_created": str(datetime.datetime.now()),
            "github_id": user_info["id"]
        }).execute()
        user_row = insert_res.data[0]
    else:
        user_row = user_data[0]

    user_row = cast(Dict[str, Any], user_row)

    request.session["user"] = {
        "id": user_row["id"],
        "email": user_row["email"],
        "name": user_row["name"],
        "picture_url": user_row["picture_url"]
    }

    return RedirectResponse(url="/pages/landing")


@router.get("/logout")
async def logout(request:Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


@router.delete("/delete")
async def deleteUser(request:Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user['id']

    try:
        supabase.table("profiles").delete().eq("id", userId).execute()
        logger.info(f"[DELTE USER] User: {userId} deleted")
    except Exception as e:
        logger.info(e)

    request.session.clear()

    return {"success": True}