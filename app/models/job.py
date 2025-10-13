from sqlalchemy import Column, Integer, String, Text, JSON
from app.core.db import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    jd_text = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)   # e.g., {"must_have": ["Python","AWS"], "min_years": 3}
    embedding = Column(JSON, nullable=True)      # list[float]
