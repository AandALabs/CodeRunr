"""
Code Execution Sandbox — FastAPI application.
"""

from fastapi import FastAPI

from routes.submissions import router as submissions_router
from routes.languages import router as languages_router
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
)


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def health():
    return {"status": "ok"}


app.include_router(languages_router, prefix=settings.API_V1_STR)
app.include_router(submissions_router, prefix=settings.API_V1_STR)
