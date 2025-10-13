from fastapi import APIRouter, HTTPException
from app.core.db import SessionLocal
from app.models.job import Job
from app.models.resume import Resume
from app.services.score_semantic import compute_semantic_score
from app.services.justify import justify

router = APIRouter()

@router.get("/justify")
async def justify_candidate(job_id: int, resume_id: int):
    db = SessionLocal()
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    r = db.query(Resume).get(resume_id)
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")

    res_obj = {"raw_text": r.raw_text, "structured": r.structured or {}, "embedding": r.embedding or []}
    job_obj = {"jd_text": job.jd_text, "requirements": job.requirements or {}, "embedding": job.embedding or []}
    sc = compute_semantic_score(res_obj, job_obj)
    facts = {
        "score_breakdown": sc["components"],
        "missing_skills": sc["missing_skills"],
        "skills": (r.structured or {}).get("skills", []),
        "experience_years_est": (r.structured or {}).get("experience_years_est", 0.0),
    }
    j = await justify(job.jd_text, r.raw_text, facts)
    return {
        "candidate_id": r.id,
        "job_id": job.id,
        "score": sc["score"],
        "breakdown": sc["components"],
        "missing_skills": sc["missing_skills"],
        "justification": j
    }
