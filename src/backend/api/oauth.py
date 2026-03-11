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



@router.get("/", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


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