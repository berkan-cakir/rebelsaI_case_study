from fastapi import APIRouter, HTTPException
import os
from app.db import get_documents_by_path,create_engine,get_job_status