from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.core.db import SessionLocal
from app.models.job import Job
from app.services.embed import embed_text

router = APIRouter()

class JobCreate(BaseModel):
    title: str
    jd_text: str
    must_have: List[str] = []
    min_years: int = 0

class JobOut(BaseModel):
    id: int
    title: str
    must_have: List[str]
    min_years: int

    class Config:
        from_attributes = True

@router.post("/create", response_model=JobOut)
def create_job(payload: JobCreate):
    db = SessionLocal()
    job = Job(
        title=payload.title,
        jd_text=payload.jd_text,
        requirements={"must_have": payload.must_have, "min_years": payload.min_years},
        embedding=embed_text(payload.jd_text),
    )
    db.add(job); db.commit(); db.refresh(job)
    return JobOut(
        id=job.id,
        title=job.title,
        must_have=job.requirements.get("must_have", []),
        min_years=job.requirements.get("min_years", 0),
    )

@router.get("/{job_id}")
def get_job(job_id: int):
    db = SessionLocal()
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "title": job.title,
        "requirements": job.requirements,
        "jd_text": job.jd_text
    }

@router.get("/")
def list_jobs():
    db = SessionLocal()
    rows = db.query(Job).all()
    return [{"id": j.id, "title": j.title, "requirements": j.requirements} for j in rows]
