# rebelsai_case_study

(AI) Document Management Endpoints – a case study in scalable API design using FastAPI, Redis, Celery, OpenAI API, and postgresql.

## Introduction
This case study / project explores building a scalable (AI) document management endpoints. Showcasing the design and implementation process of two endpoints: folder insight and document classification analyses.

## Features

Folder insight:
- Provide information on the total number of documents in the folder.
- Extract and present relevant metadata associated with the documents.

Document classification analyses:
- Utilise an open-source generative AI model or OpenAI API for document classification.

## Techstack

- Python
- fastAPI
- Redis (Queue)
- Celery
- PostGreSQL
- openAI API
- sqlalchemy

## Setup

The API and related docker services can be setup with a single command:

```docker-compose up --build```

After running the command, one can interact with the API through the fastAPI interactive docs by going to:

```http://127.0.0.1:8000/docs```

If any errors show up during initialization, close docker using ctrl+c and run docker-compose up command again.

## Usage

See fastAPI interactive docs.

Note that /folder-insights/{folder_path}/get_folder_files_metadata must be called before either Document Classification endpoint api endpoints.

For the Document Classification endpoint to work, you will need to add a .env with OPENAI_API_KEY="sk-proj-XXXX" to root.

## Design

This project is designed around scalable, fault tolerant, asynchronous document processing pipeline. The goal is to support ingestion, metadata extraction, and analyses through tagging and summurization of large sets of (docx) documents.

# Components
- FastAPI (API layer)
    - Provides rest endpoints for folder/document operations.
    - Handles incoming requests and immediately responds to clients without waiting for long-running jobs.
    - Delegates heavy work (metadata extraction, LLM calls) to celery workers via Redis.
- Celery (Task queue)
    - Executes background jobs asynchronously.
    - Supports parallelism by running multiple workers (by increasing the number of celery worker services via docker compose).
    - Can support jobs to be retried on failure and status to be tracked.
- Redis (Message broker)
    - Serves as the broker between FastAPI and Celery
    - Stores queued tasks until a celery worker picks them up.
- PostgreSQL (Database)
    - Persists document metadata.
    - Stores job history and processing status.
- OpenAI API (LLM integration)
    - Used for document processing.
    - Called via celery task workers to be able to retry requests and parallize.
- Docker + Docker Compose
    - Each service (API, celery worker, Redis, Postgres) runs in its own container.
    - Compose manages multi-container locally.
    - Ready to be scaled horizontally with Kubernetes and Ngninx load balancer for production.
## Scalability Notes
- Asynchronous task queue - Celery ensures long-running LLM calls don’t block API responses.
- Parallelism - Multiple Celery workers process documents in parallel. Which can be scaled automatically with Kubernetes during high load/traffic.
- Horizontal scaling - FastAPI and Celery workers can be replicated; load balancer distributes traffic.
- Caching and Idempotency - Database prevents duplicate work (e.g., don’t re-summarize documents that already have summaries).
- Future-proof - Can scale from Docker Compose (dev) - Kubernetes (prod).

## Improvements (outside scope for case study)

- minIO buckets for client data
- Rate limiting
- User privileges
- Kubernetes & Nnginx load balancer for horizontal scalling
