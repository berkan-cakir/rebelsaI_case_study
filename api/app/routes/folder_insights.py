from fastapi import APIRouter, HTTPException
from app.db import get_folder_count, create_job
from app.tasks import update_folder_count
import os

router = APIRouter()
BASE_PATH = os.path.join(os.path.dirname(__file__), "Client Data")

@router.get("/{folder_path:path}/count_files")
async def folder_count(folder_path: str):
    # full_path = os.path.normpath(os.path.join(BASE_PATH, folder_path))
    # if not full_path.startswith(BASE_PATH):
    #     raise HTTPException(status_code=400, detail="Invalid folder path")

    # li = os.listdir(full_path)  # Debug line to check if BASE_PATH is correct

    # files = [f for f in os.listdir(full_path)]
    # return {"files": files}

    try:
        full_path = os.path.normpath(os.path.join(BASE_PATH, folder_path))
        if not full_path.startswith(BASE_PATH):
            raise HTTPException(status_code=400, detail="Invalid folder path")

        count = get_folder_count(full_path)
        if count is not None:
            return {"folder_path": folder_path, "document_count": count}

        # if not os.path.exists(folder_path):
        #     raise HTTPException(status_code=404, detail="Folder not found")
        
        job_id = create_job(status="PENDING")
        update_folder_count.delay(job_id, full_path)

        return {"folder_path": folder_path, "job_id": job_id, "status": "Job started to count documents"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))