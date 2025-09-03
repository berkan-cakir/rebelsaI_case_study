from fastapi import APIRouter, HTTPException
import os
from app.db import get_documents_in_folder, create_job, check_document_tagged, check_document_summarized, get_document_id_by_path
from app.tasks import tag_documents_task, summarize_document

router = APIRouter()
BASE_PATH = os.path.join(os.path.dirname(__file__), "Client Data")

@router.get("/{folder_path:path}/tag_documents")
async def tag_documents(folder_path: str):
    """Tag all .docx documents in the specified folder."""
    try:
        full_path = os.path.normpath(os.path.join(BASE_PATH, folder_path))
        if not full_path.startswith(BASE_PATH):
            raise HTTPException(status_code=400, detail="Invalid folder path")
        elif not os.path.exists(full_path) or not os.path.isdir(full_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        
        files = [
            f for f in os.listdir(full_path)
            if f.endswith(".docx") and os.path.isfile(os.path.join(full_path, f))
        ]

        if not files:
            return {"folder_path": folder_path, "status": "No documents found in folder"}

        jobs_ids = []
        for file in files:
            file_path = os.path.join(full_path, file)

            print(f"Checking tagging for {file_path}")  # Debugging line

            if not check_document_tagged(file_path):
                print(f"Tagging document: {file_path}")  # Debugging line

                job_id = create_job(status="PENDING")
                print(f"Created job {job_id} for {file_path}")  # Debugging line
                document_id = get_document_id_by_path(file_path)
                print(f"Document ID for {file_path} is {document_id}")

                result = tag_documents_task.delay(job_id, document_id, file_path)
                print(f"Dispatched tagging task for job {job_id}, result: {result}")  # Debugging line
                jobs_ids.append(job_id)

        if jobs_ids:
            return {"folder_path": folder_path,
                    "job_ids": jobs_ids,
                    "status": f"Tagging jobs started for {len(jobs_ids)} untagged documents"}
        else:
            return {"folder_path": folder_path,
                    "status": "All documents already tagged"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{folder_path:path}/summarize_documents")
async def summarize_documents(folder_path: str):
    """Summarize all .docx documents in the specified folder."""
    try:
        full_path = os.path.normpath(os.path.join(BASE_PATH, folder_path))
        if not full_path.startswith(BASE_PATH):
            raise HTTPException(status_code=400, detail="Invalid folder path")
        elif not os.path.exists(full_path) or not os.path.isdir(full_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        
        files = [
            f for f in os.listdir(full_path)
            if f.endswith(".docx") and os.path.isfile(os.path.join(full_path, f))
        ]

        if not files:
            return {"folder_path": folder_path, "status": "No documents found in folder"}

        jobs_ids = []
        for file in files:
            file_path = os.path.join(full_path, file)

            if not check_document_summarized(file_path):
                job_id = create_job(status="PENDING")
                summarize_document.delay(job_id, file_path)
                jobs_ids.append(job_id)
        
        if jobs_ids:
            return {"folder_path": folder_path,
                    "job_ids": jobs_ids,
                    "status": f"Summarization jobs started for {len(files)} unsummarized documents"}
        else:
            return {"folder_path": folder_path,
                    "status": "All documents already summarized"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
