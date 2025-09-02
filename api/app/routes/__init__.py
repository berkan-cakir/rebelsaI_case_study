from fastapi import APIRouter
from .folder_insights import router as folder_insights_router
from .document_classification import router as document_classification_router

router = APIRouter()
router.include_router(folder_insights_router, prefix="/folder-insights", tags=["Folder Insights"])
router.include_router(document_classification_router, prefix="/document-classification", tags=["Document Classification"])