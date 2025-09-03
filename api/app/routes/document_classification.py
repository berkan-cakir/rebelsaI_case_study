from fastapi import APIRouter, HTTPException
import os
from openai import OpenAI

client = OpenAI()
router = APIRouter()
BASE_PATH = os.path.join(os.path.dirname(__file__), "Client Data")

@router.get("/{folder_path:path}/tag_documents")
async def tag_documents(folder_path: str):
    """comment"""
    try:
        full_path = os.path.normpath(os.path.join(BASE_PATH, folder_path))
        if not full_path.startswith(BASE_PATH):
            raise HTTPException(status_code=400, detail="Invalid folder path")
        elif not os.path.exists(full_path) or not os.path.isdir(full_path):
            raise HTTPException(status_code=404, detail="Folder not found")

        # Placeholder for document classification logic
        return {"folder_path": folder_path, "status": "Document classification not yet implemented"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{folder_path:path}/summarize_documents")
async def summarize_documents(folder_path: str):
    """comment"""
    try:
        full_path = os.path.normpath(os.path.join(BASE_PATH, folder_path))
        if not full_path.startswith(BASE_PATH):
            raise HTTPException(status_code=400, detail="Invalid folder path")
        elif not os.path.exists(full_path) or not os.path.isdir(full_path):
            raise HTTPException(status_code=404, detail="Folder not found")

        # Placeholder for document summarization logic
        return {"folder_path": folder_path, "status": "Document summarization not yet implemented"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))