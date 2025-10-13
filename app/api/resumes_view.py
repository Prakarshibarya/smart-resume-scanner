from fastapi import APIRouter, HTTPException
from app.core.db import SessionLocal
from app.models.resume import Resume
from app.services.extract import extract_structured

router = APIRouter()

@router.get("/{resume_id}")
def get_resume(resume_id: int):
    db = SessionLocal()
    r = db.query(Resume).get(resume_id)
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "id": r.id,
        "structured": r.structured,
        "chars": len(r.raw_text or ""),
    }

@router.post("/reextract/{resume_id}")
def reextract_resume(resume_id: int):
    db = SessionLocal()
    r = db.query(Resume).get(resume_id)
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    r.structured = extract_structured(r.raw_text or "")
    db.add(r); db.commit(); db.refresh(r)
    return {"id": r.id, "structured": r.structured}
