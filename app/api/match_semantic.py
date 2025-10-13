from fastapi import APIRouter, HTTPException
from app.core.db import SessionLocal
from app.models.job import Job
from app.models.resume import Resume
from app.services.score_semantic import compute_semantic_score

router = APIRouter()

@router.get("/shortlist_semantic")
def shortlist_semantic(job_id: int, k: int = 5):
    db = SessionLocal()
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resumes = db.query(Resume).all()
    results = []
    for r in resumes:
        res_obj = {
            "raw_text": r.raw_text,
            "structured": r.structured or {},
            "embedding": r.embedding or [],
        }
        job_obj = {
            "jd_text": job.jd_text,
            "requirements": job.requirements or {},
            "embedding": job.embedding or [],
        }
        s = compute_semantic_score(res_obj, job_obj)
        results.append({
            "candidate_id": r.id,
            "candidate_name": r.candidate_name,
            "structured": r.structured,
            "score": s["score"],
            "breakdown": s["components"],
            "missing_skills": s["missing_skills"],
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max(1, k)]
