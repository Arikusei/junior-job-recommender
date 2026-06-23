from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


class AbVariant(str, Enum):
    CONTROL = "control"
    TREATMENT = "treatment"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    skills: Mapped[str] = mapped_column(String(300))
    city: Mapped[str] = mapped_column(String(80))
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grade: Mapped[str] = mapped_column(String(40), default="junior")
    views: Mapped[int] = mapped_column(Integer, default=0)
    applications: Mapped[int] = mapped_column(Integer, default=0)

    events: Mapped[list["UserEvent"]] = relationship(back_populates="job")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    resume_text: Mapped[str] = mapped_column(Text)
    skills: Mapped[str] = mapped_column(String(300))
    ab_variant: Mapped[str] = mapped_column(String(20), default=AbVariant.CONTROL.value)

    events: Mapped[list["UserEvent"]] = relationship(back_populates="user")


class UserEvent(Base):
    __tablename__ = "user_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profiles.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    event_type: Mapped[str] = mapped_column(String(40))
    ab_variant: Mapped[str] = mapped_column(String(20))
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[UserProfile] = relationship(back_populates="events")
    job: Mapped[Job] = relationship(back_populates="events")


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
