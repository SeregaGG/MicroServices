import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api import agent

from app.core.config import settings

load_dotenv()
service_name = os.getenv('SERVICE_NAME', 'test')

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"/{service_name}{settings.API_V1_STR}/openapi.json",
)

app.include_router(agent.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Hello World"}

import uvicorn


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)