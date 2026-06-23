from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import Job, UserEvent, UserProfile, get_db, init_db
from app.recommender import (
    ab_stats,
    assign_ab_group,
    load_index,
    recommend_for_user,
    search_jobs,
)

# счётчики для /metrics — сделал по туториалу prometheus
request_count = {"recommend": 0, "search": 0, "clicks": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_index()  # faiss индекс
    yield


app = FastAPI(title="job-recommender", lifespan=lifespan)


class SearchBody(BaseModel):
    query: str
    top_k: int = 10


class EventBody(BaseModel):
    user_id: int
    job_id: int
    event_type: str
    position: int | None = None


@app.get("/")
def root():
    return {"msg": "job recommender api", "docs": "/docs"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@app.get("/users/{user_id}/recommendations")
def recommendations(user_id: int, top_k: int = 10, db: Session = Depends(get_db)):
    user = db.get(UserProfile, user_id)
    if not user:
        raise HTTPException(404, "user not found")

    if not user.ab_variant:
        user.ab_variant = assign_ab_group(user_id)
        db.commit()

    request_count["recommend"] += 1
    recs = recommend_for_user(db, user, top_k)

    response = []
    for pos, (job, score) in enumerate(recs, start=1):
        # пишем показ в бд для ab теста
        db.add(
            UserEvent(
                user_id=user.id,
                job_id=job.id,
                event_type="impression",
                ab_variant=user.ab_variant,
                position=pos,
                score=score,
            )
        )
        job.views += 1
        response.append(
            {
                "position": pos,
                "score": round(score, 3),
                "variant": user.ab_variant,
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "city": job.city,
                    "skills": job.skills,
                },
            }
        )
    db.commit()
    return response


@app.post("/search")
def search(body: SearchBody, db: Session = Depends(get_db)):
    request_count["search"] += 1
    results = search_jobs(db, body.query, body.top_k)
    return [
        {
            "score": round(score, 3),
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "skills": job.skills,
            },
        }
        for job, score in results
    ]


@app.post("/events")
def track_event(body: EventBody, db: Session = Depends(get_db)):
    user = db.get(UserProfile, body.user_id)
    job = db.get(Job, body.job_id)
    if not user or not job:
        raise HTTPException(404, "not found")

    db.add(
        UserEvent(
            user_id=user.id,
            job_id=job.id,
            event_type=body.event_type,
            ab_variant=user.ab_variant or assign_ab_group(user.id),
            position=body.position,
        )
    )
    if body.event_type == "click":
        job.applications += 1
        request_count["clicks"] += 1
    db.commit()
    return {"status": "ok"}


@app.get("/ab/stats")
def get_ab_stats(db: Session = Depends(get_db)):
    return ab_stats(db)


@app.get("/metrics")
def metrics():
    # не полноценный prometheus, но для пет-проекта хватит
    lines = [f"recommend_requests {request_count['recommend']}"]
    lines.append(f"search_requests {request_count['search']}")
    lines.append(f"click_events {request_count['clicks']}")
    return "\n".join(lines)
