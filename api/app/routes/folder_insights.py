from fastapi import APIRouter, HTTPException
from app.db import get_folder_count, create_job, get_documents_metadata_in_folder
from app.tasks import update_folder_count, update_folder_files_metadata
import os

router = APIRouter()
BASE_PATH = os.path.join(os.path.dirname(__file__), "Client Data")

@router.get("/{folder_path:path}/count_files")
async def folder_count(folder_path: str):
    """Count .docx files in the specified folder and return the cached count or start a job."""
    try:
        full_path = os.path.normpath(os.path.join(BASE_PATH, folder_path))
        if not full_path.startswith(BASE_PATH):
            raise HTTPException(status_code=400, detail="Invalid folder path")
        elif not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="Folder not found")

        count = get_folder_count(full_path)
        if count is not None:
            return {"folder_path": folder_path, "document_count": count}
        
        job_id = create_job(status="PENDING")
        update_folder_count.delay(job_id, full_path)

        return {"folder_path": folder_path, "job_id": job_id, "status": "Job started to count documents"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/{folder_path:path}/get_folder_files_metadata")
async def get_file_metadata(folder_path: str, limit: int = 10):
    """Retrieve cached metadata for files in the folder or start a job to insert metadata."""
    try:
        full_path = os.path.normpath(os.path.join(BASE_PATH, folder_path))
        if not full_path.startswith(BASE_PATH):
            raise HTTPException(status_code=400, detail="Invalid folder path")
        elif not os.path.exists(full_path) or not os.path.isdir(full_path):
            raise HTTPException(status_code=404, detail="Folder not found")

        files = get_documents_metadata_in_folder(full_path, limit)
        if files:
            return {"folder_path": folder_path, "files": files}

        job_id = create_job(status="PENDING")
        update_folder_files_metadata.delay(job_id, full_path)
        
        return {"folder_path": folder_path, "job_id": job_id, "status": "Jobs started to insert document metadata"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))