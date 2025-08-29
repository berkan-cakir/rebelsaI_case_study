from .document_classification import router as document_classification_router
from .folder_insights import router as folder_insights_router

routers = [ document_classification_router, folder_insights_router]