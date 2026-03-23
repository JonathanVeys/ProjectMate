from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from ..utils.supabase_client import supabase
from ..utils.utils import get_current_user


router = APIRouter(prefix="/user", tags=["user"])



@router.get("/avatar/{user_id}")
async def get_user_avatar(user_id:str, current_user=Depends(get_current_user)):
    res = supabase.table("profiles").select("picture_url").eq("user_id", user_id).execute()

    if res.data[0]:
        return res.data[0]["picture_url"]
    else:
        raise HTTPException(400, "Error in getting user avatar")
