from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from . import upload, oauth


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="a-very-secret-key",  # change this to something secure in production
)


@app.get("/")
def root():
    return {"message": "✅ ProjectMate API is running!"}


app.include_router(upload.router)
app.include_router(oauth.router)
