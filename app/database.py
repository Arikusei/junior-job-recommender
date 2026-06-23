from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from app.config import DATABASE_URL

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    company = Column(String(120))
    description = Column(Text)
    skills = Column(String(300))
    city = Column(String(80))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    grade = Column(String(40), default="junior")
    views = Column(Integer, default=0)
    applications = Column(Integer, default=0)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    resume_text = Column(Text)
    skills = Column(String(300))
    ab_variant = Column(String(20), nullable=True)


class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    event_type = Column(String(40))  # impression / click
    ab_variant = Column(String(20))
    position = Column(Integer)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile")
    job = relationship("Job")


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
