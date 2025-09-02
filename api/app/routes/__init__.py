from fastapi import APIRouter
from .folder_insights import router as folder_insights_router

router = APIRouter()
router.include_router(folder_insights_router, prefix="/folder-insights", tags=["Folder Insights"])