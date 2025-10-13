import re
import yaml
from pathlib import Path
from typing import Dict, List, Set

# Load ontology once
_ONT_PATH = Path("app/data/skills_ontology.yaml")
_ONTOLOGY = yaml.safe_load(_ONT_PATH.read_text(encoding="utf-8"))

# Build a map of lowercase term -> canonical name
_CANON: Dict[str, str] = {}
for domain, items in _ONTOLOGY.items():
    for it in items:
        canon = it["name"]
        _CANON[canon.lower()] = canon
        for a in it.get("aliases", []):
            _CANON[str(a).lower()] = canon

_WORD = r"[A-Za-z0-9\.\+\#\-]+"

def _tokens(text: str) -> List[str]:
    return re.findall(_WORD, text.lower())

def _normalize_skills(text: str) -> Set[str]:
    toks = _tokens(text)
    joined = " ".join(toks)

    found: Set[str] = set()

    # 1) phrase/alias matching (prefer multi-word first)
    phrases = sorted(_CANON.keys(), key=lambda s: len(s), reverse=True)
    for p in phrases:
        # flexible word-boundary-ish match
        pat = r"(?<![A-Za-z0-9])" + re.escape(p) + r"(?![A-Za-z0-9])"
        if re.search(pat, joined):
            found.add(_CANON[p])

    return found

def _extract_years(text: str) -> float:
    # finds patterns like "3 years", "5+ yrs", "2yr", etc.
    yrs = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)", text, flags=re.I):
        try:
            yrs.append(float(m.group(1)))
        except ValueError:
            pass
    return round(max(yrs), 1) if yrs else 0.0

def extract_structured(raw_text: str) -> Dict:
    if not raw_text:
        return {"skills": [], "experience_years_est": 0.0, "education": []}

    skills = sorted(_normalize_skills(raw_text))
    years = _extract_years(raw_text)

    # (simple placeholder) collect education lines mentioning university/college/institute
    edu = []
    for line in raw_text.splitlines():
        L = line.strip()
        if re.search(r"(university|college|institute|iit|iiit|nit|vit)", L, flags=re.I):
            edu.append(L)
            if len(edu) >= 5:
                break

    return {"skills": skills, "experience_years_est": years, "education": edu}
