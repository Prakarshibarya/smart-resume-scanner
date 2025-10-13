from typing import Dict, Set
from app.services.embed import cosine

def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))

def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x

def compute_semantic_score(resume: Dict, job: Dict, weights: Dict[str, float] | None = None) -> Dict:
    """
    resume: { raw_text, structured:{skills, experience_years_est}, embedding }
    job:    { requirements:{must_have, min_years}, embedding, jd_text }
    """
    w = {"sem": 0.45, "skills": 0.30, "exp": 0.20, "gap": 0.05}
    if weights: w.update(weights)

    # semantic cosine
    sem = cosine(resume.get("embedding", []), job.get("embedding", []))

    # skills match
    rskills = set((resume.get("structured") or {}).get("skills", []))
    need = set((job.get("requirements") or {}).get("must_have", []))
    skills_match = jaccard(rskills, need)

    # experience ratio
    have = float((resume.get("structured") or {}).get("experience_years_est", 0.0) or 0.0)
    req = float((job.get("requirements") or {}).get("min_years", 0) or 0.0)
    exp_ratio = 1.0 if req == 0 else clamp01(have / max(1.0, req))

    missing = sorted(list(need - rskills))
    gap_pen = 0.0 if not need else clamp01(len(missing) / max(1, len(need)))

    raw = (w["sem"]*sem + w["skills"]*skills_match + w["exp"]*exp_ratio - w["gap"]*gap_pen)
    score100 = max(0.0, min(100.0, 100.0 * raw))

    return {
        "score": round(score100, 1),
        "components": {
            "semantic": round(sem, 3),
            "skills_match": round(skills_match, 3),
            "exp_ratio": round(exp_ratio, 3),
            "gap_penalty": round(gap_pen, 3),
        },
        "missing_skills": missing
    }
