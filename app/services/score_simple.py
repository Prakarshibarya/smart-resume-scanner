import re
from typing import List, Dict

def _find_experience_years(text: str) -> float:
    """
    Very naive: looks for patterns like '3 years', '5+ years', '7 yrs'.
    Returns the max number found, or 0 if none.
    """
    if not text:
        return 0.0
    years = []
    for m in re.finditer(r'(\d+)\s*\+?\s*(year|years|yr|yrs)', text, flags=re.I):
        try:
            years.append(float(m.group(1)))
        except:
            pass
    return max(years) if years else 0.0

def simple_score(raw_text: str, must_have: List[str], min_years: int) -> Dict:
    """
    Score = 70% skills match + 30% experience ratio (clipped)
    """
    rt = raw_text.lower() if raw_text else ""
    mh = [s.lower() for s in (must_have or [])]
    found = []
    for skill in mh:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, rt, flags=re.I):
            found.append(skill)
        else:
            if skill in rt:
                found.append(skill)

    skills_ratio = (len(found) / max(1, len(mh))) if mh else 1.0
    have_years = _find_experience_years(rt)
    exp_ratio = min(1.0, have_years / max(1, min_years)) if min_years else 1.0

    score = 100.0 * (0.70 * skills_ratio + 0.30 * exp_ratio)
    missing = [s for s in mh if s not in found]

    return {
        "score": round(score, 1),
        "skills_ratio": round(skills_ratio, 3),
        "exp_ratio": round(exp_ratio, 3),
        "have_years": have_years,
        "min_years": min_years,
        "found_skills": sorted(found),
        "missing_skills": sorted(missing),
    }
