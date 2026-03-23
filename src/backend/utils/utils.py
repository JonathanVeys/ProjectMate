from fastapi import Header, HTTPException

from .supabase_client import supabase

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    access_token = authorization.split(" ", 1)[1]

    # verify token with Supabase
    user_response = supabase.auth.get_user(access_token)
    if user_response:
        user = user_response.user

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user