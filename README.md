### Smart Resume Screener

An AI-powered resume parsing and job-fit analysis system built with **FastAPI**, **Streamlit**, and **Sentence-Transformers**.  
It parses resumes (PDF/DOCX/TXT), extracts skills and experience, performs **semantic matching** against job descriptions, and produces **LLM-based explanations** — all while redacting personal information for privacy.
---

## Demo Video link
https://drive.google.com/file/d/1mWZNriPqdaOieNOsn7xUVugOb7M9cBwD/view?usp=drive_link

---

## Features
~ Resume parsing (PDF/DOCX/TXT)  
~ Skill & experience extraction  
~ Semantic matching using Sentence-Transformers  
~ Weighted scoring (semantic + skills + experience)  
~ LLM justification (mock or real GPT)  
~ Streamlit dashboard with CSV export  

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| **Backend** | FastAPI · SQLAlchemy · SQLite |
| **ML / NLP** | Sentence-Transformers · regex · ontology |
| **LLM** | OpenAI-compatible `/chat/completions` API |
| **Frontend** | Streamlit |
| **Infra** | Localhost / Docker-ready |

---

## Architecture

```text
          ┌───────────────┐       ┌─────────────┐
Resume →  │ /resumes      │       │ /jobs       │  ← JD text
(PDF etc) │ Upload/Parse  │       │ Create/List │
          └──────┬────────┘       └──────┬──────┘
                 │                        │
                 ▼                        ▼
         ┌────────────┐          ┌────────────┐
         │ Extraction │          │ Embedding  │ (JD)
         │ skills/exp │          └────────────┘
         └─────┬──────┘                │
               ▼                        ▼
         ┌────────────┐          ┌────────────┐
         │ Embedding  │          │  Matching  │
         │ (resume)   │          │ (semantic+ │
         └─────┬──────┘          │  skills)   │
               ▼                 └─────┬──────┘
                     ┌────────────────┴──────────────┐
                     │   Ranked shortlist JSON        │
                     └────────────────┬───────────────┘
                                      ▼
                            ┌────────────────────┐
                            │ LLM justification  │
                            │ (PII-redacted)     │
                            └────────┬───────────┘
                                     ▼
                            Streamlit Dashboard

```

---
## Setup
```bash
# create venv
py -3 -m venv .venv
.venv\Scripts\activate

# install deps
pip install -r requirements.txt

# run backend
python -m uvicorn app.main:app --reload --port 8000

# run UI (new terminal)
streamlit run dashboard/app.py

```
---
## Scoring Formula
score = 100 * (
    0.45 * semantic_cosine + 0.30 * jaccard(skills) + 0.20 * experience_ratio - 0.05 * gap_penalty
)



## LLM Prompt Design 
You are an ATS assistant. Return ONLY JSON with keys:
fit_on_10, why, strengths, gaps.
Base your answer only on supplied facts (already PII-redacted).

## User Template
Job Description:
{jd}

Resume:
{resume}

Extracted Facts:
{facts}

Task:
Rate the candidate fit (1-10), explain briefly why,
list 3 strengths and up to 5 gaps.
Return pure JSON only.

## Example Output
{
  "fit_on_10": 8,
  "why": "Strong ML and NLP background, minor gap in cloud experience",
  "strengths": ["Python", "Transformers", "Project leadership"],
  "gaps": ["AWS deployment", "CI/CD", "Team mentoring"]
}



