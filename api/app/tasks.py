import os
from celery import Celery
from app.db import update_job, upsert_folder_count, get_tags_for_document
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