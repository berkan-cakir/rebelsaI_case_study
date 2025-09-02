import os
from datetime import datetime
from celery import Celery
from app.db import update_job, upsert_folder_count, create_job, insert_document
from openai import OpenAI

celery = Celery('app', broker='redis://redis:6379/0', include=['app.tasks']
)

@celery.task
def update_folder_count(job_id: int, path: str):
    """
    Only count .docx files in the folder and update `folders` table.
    Does not insert document metadata.
    """
    try:
        files = [
            f for f in os.listdir(path)
            if f.endswith(".docx") and os.path.isfile(os.path.join(path, f))
        ]
        count = len(files)

        upsert_folder_count(path, count, job_id)
        update_job(job_id, status="done", result=f"Counted {count} documents")
        return f"Counted {count} documents"

    except Exception as e:
        update_job(job_id, status="failed", result=str(e), doc_count=0)
        raise

@celery.task
def update_folder_files_metadata(job_id: int, path: str):
    """
    Process the folder to extract metadata for each .docx file and insert into `documents` table.
    """
    try:
        files = [f for f in os.listdir(path)]

        for file in files:
            filepath = os.path.join(path, file)
            size_kb = os.path.getsize(filepath) / 1024
            modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            file_job_id = create_job(status="PENDING")
            insert_document(file_job_id, filepath, file, size_kb, modified_time)
            update_job(file_job_id, status="done", result="Inserted document metadata")

        update_job(job_id, status="done", result=f"Inserted metadata for {len(files)} documents")
        return f"Inserted metadata for {len(files)} documents"

    except Exception as e:
        update_job(job_id, status="failed", result=str(e))
        raise