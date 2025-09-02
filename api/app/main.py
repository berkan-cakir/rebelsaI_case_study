from fastapi import FastAPI
from app.routes import router  # Import the routers list
from app.db import init_db

app = FastAPI(title="Document Management API")

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(router)