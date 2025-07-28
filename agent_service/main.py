from fastapi import FastAPI

from  app.api import agent

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(agent.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Hello World"}