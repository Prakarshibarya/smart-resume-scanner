import os, json, httpx
from app.services.redact import redact

SYSTEM = "You are an ATS assistant. Return ONLY JSON keys: fit_on_10, why, strengths, gaps."
USER_TMPL = """Job Description:
{jd}

Resume:
{resume}

Extracted Facts:
{facts}

Task:
Rate the candidate fit from 1-10 (integer), explain briefly why, list 3 strengths, up to 5 gaps.
Return pure JSON only.
"""

def _mock(facts: dict) -> dict:
    ms = facts.get("missing_skills", [])
    fit = max(1, 10 - min(5, len(ms)))
    return {
        "fit_on_10": fit,
        "why": "Good overlap with role; remaining gaps are limited and addressable.",
        "strengths": facts.get("strengths", ["Relevant skills present","Experience aligns","Solid projects"]),
        "gaps": ms[:5],
    }

async def justify(jd_text: str, resume_text: str, facts: dict) -> dict:
    base = os.getenv("LLM_API_BASE")
    key  = os.getenv("LLM_API_KEY")
    model= os.getenv("LLM_MODEL", "gpt-4o-mini")

    jd_r = redact(jd_text or "")
    rv_r = redact(resume_text or "")
    user = USER_TMPL.format(jd=jd_r, resume=rv_r, facts=json.dumps(facts, ensure_ascii=False))

    if not base or not key:
        return _mock(facts)

    try:
        async with httpx.AsyncClient(base_url=base, headers={"Authorization": f"Bearer {key}"}, timeout=60) as c:
            payload = {"model": model, "temperature": 0.2,
                       "messages": [{"role":"system","content":SYSTEM},
                                    {"role":"user","content":user}]}
            r = await c.post("/chat/completions", json=payload)
            r.raise_for_status()
            txt = r.json()["choices"][0]["message"]["content"]
            return json.loads(txt)
    except Exception:
        return _mock(facts)
