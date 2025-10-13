from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from datetime import datetime
from app.core.db import Base

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, index=True, nullable=True)
    raw_text = Column(Text, nullable=True)
    structured = Column(JSON, nullable=True)   # e.g., {"skills":[], "experience_years_est": 3.0, "education":[]}
    embedding = Column(JSON, nullable=True)    # list[float]
    created_at = Column(DateTime, default=datetime.utcnow)
