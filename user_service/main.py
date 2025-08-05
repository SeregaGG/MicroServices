import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api import users, auth
from app.core.config import settings

load_dotenv()
service_name = os.getenv('SERVICE_NAME')

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"/{service_name}/{settings.API_V1_STR}/openapi.json",
)

app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Hello World"}