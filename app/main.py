from fastapi import FastAPI
from sqlalchemy import inspect
from app.core.db import engine, Base

from app.models.resume import Resume  # noqa
from app.models.job import Job        # noqa

from app.api import resumes
from app.api import jobs   
from app.api import match
from app.api import resumes_view
from app.api import match_semantic
from app.api import explain

app = FastAPI(title="Smart Resume Screener")
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug/tables")
def list_tables():
    insp = inspect(engine)
    return {"tables": insp.get_table_names()}

app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
app.include_router(resumes_view.router, prefix="/resumes/view", tags=["resumes"])
app.include_router(jobs.router,    prefix="/jobs",    tags=["jobs"])   
app.include_router(match.router,   prefix="/match",   tags=["match"])
app.include_router(match_semantic.router, prefix="/match", tags=["match"])
app.include_router(explain.router, prefix="/match", tags=["match"])