from fastapi import APIRouter, HTTPException
from typing import List
from app.core.db import SessionLocal
from app.models.job import Job
from app.models.resume import Resume
from app.services.score_simple import simple_score

router = APIRouter()

@router.get("/shortlist")
def shortlist(job_id: int, k: int = 5):
    db = SessionLocal()
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    must_have = (job.requirements or {}).get("must_have", [])
    min_years = (job.requirements or {}).get("min_years", 0)

    rows = db.query(Resume).all()
    results = []
    for r in rows:
        s = simple_score(r.raw_text or "", must_have, min_years)
        results.append({
            "candidate_id": r.id,
            "candidate_name": r.candidate_name,
            "structured": r.structured,
            "score": s["score"],
            "breakdown": {
                "skills_ratio": s["skills_ratio"],
                "exp_ratio": s["exp_ratio"],
                "have_years": s["have_years"],
                "min_years": s["min_years"],
                "found_skills": s["found_skills"],
                "missing_skills": s["missing_skills"],
            }
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max(1, k)]
