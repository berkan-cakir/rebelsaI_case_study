import os
from datetime import datetime
from celery import Celery
from app.db import update_job, upsert_folder_count, create_job, insert_document, get_all_tags, insert_tag_document, add_summary_for_document
from openai import OpenAI
from app.preprocessing import extract_text_from_docx
import json

OpenAI.api_key = os.getenv("OPENAI_API_KEY")

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

@celery.task
def tag_documents_task(job_id: int, document_id: int, path: str):
    """
    Placeholder for document tagging logic using OpenAI.
    """
    try:
        client = OpenAI()
        text = extract_text_from_docx(path)
        all_tags = get_all_tags()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert document classifier. "
                        "Given the content of a document, assign the most relevant tags "
                        "from the provided list. Only select tags that are clearly applicable."
                        "Make sure you write the summary only in Dutch."
                        "Do not add any prefixes or suffixes to the summary."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Document Content:\n{text}\n\n"
                        f"Available Tags: {', '.join(all_tags)}\n\n"
                        "Return the tags as a JSON array."
                    )
                }
            ],
            max_tokens=150,
            temperature=0
        )
        tags = response.choices[0].message.content
        tags = json.loads(tags)

        print(f"Tags for document {document_id}: {tags}")

        for tag in tags:
            print(f"Inserting tag '{tag}' for document ID {document_id}")  # Debugging line
            insert_tag_document(document_id, tag)

        update_job(job_id, status="done", result=f"Tagged document with {len(tags)} tags")
        return f"Tagged document with {len(tags)} tags"

    except Exception as e:
        update_job(job_id, status="failed", result=str(e))
        raise

@celery.task
def summarize_document(job_id: int, path: str):
    """
    Placeholder for document summarization logic using OpenAI.
    """
    try:
        client = OpenAI()
        text = extract_text_from_docx(path)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert document summarizer. "
                        "Given the content of a document, provide a concise summary "
                        "highlighting the key points."
                        "Make sure you write the summary only in Dutch."
                        "Do not add any prefixes or suffixes to the summary."
                    )
                },
                {
                    "role": "user",
                    "content": f"Document Content:\n{text}\n\nProvide a concise summary."
                }
            ],
            max_tokens=150,
            temperature=0
        )
        summary = response.choices[0].message.content
        print(f"Summary: {summary}")

        add_summary_for_document(path, summary)
        update_job(job_id, status="done", result="Added document summary")

        return "Added document summary"

    except Exception as e:
        update_job(job_id, status="failed", result=str(e))
        raise