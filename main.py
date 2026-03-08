"""
Code Execution Sandbox — FastAPI application.
"""

from fastapi import FastAPI
from routes import api_router
from config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
)


app.include_router(api_router)
