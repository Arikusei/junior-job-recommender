from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.models import Job, SessionLocal, UserEvent, UserProfile


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_user(db: Session, user_id: int) -> UserProfile:
    user = db.get(UserProfile, user_id)
    if user is None:
        raise LookupError(f"User {user_id} not found")
    return user


def list_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()


def record_event(
    db: Session,
    *,
    user_id: int,
    job_id: int,
    event_type: str,
    ab_variant: str,
    position: int | None = None,
    score: float | None = None,
) -> UserEvent:
    event = UserEvent(
        user_id=user_id,
        job_id=job_id,
        event_type=event_type,
        ab_variant=ab_variant,
        position=position,
        score=score,
    )
    db.add(event)

    job = db.get(Job, job_id)
    if job and event_type == "impression":
        job.views += 1
    if job and event_type == "click":
        job.applications += 1

    db.commit()
    db.refresh(event)
    return event
