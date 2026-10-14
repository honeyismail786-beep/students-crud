from fastapi import FastAPI

from app import models  # noqa: F401  (registers the Student table)
from app.database import Base, engine
from app.routers import ai, students

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Students Database API",
    description="CRUD API for managing student records (FastAPI + SQLite).",
    version="1.0.0",
)

app.include_router(students.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Students API is running"}