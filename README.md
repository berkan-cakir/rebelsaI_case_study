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
- Redis Queue
- Celery
- PostGreSQL
- openAI API

## Setup

The API can be setup with a single command:
```docker-compose up --build```

After running the command, one can interact with the API through the fastAPI interactive docs by going to: ```http://127.0.0.1:8000/docs```

## Usage

## Design

## Scalability Notes

## Conclusions / Case Study Notes