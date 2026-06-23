from __future__ import annotations

import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from prometheus_client import generate_latest
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.ab.analysis import compute_ab_stats
from app.ab.experiment import ensure_user_variant
from app.db.models import Job, UserProfile
from app.db.repository import record_event
from app.monitoring.metrics import (
    EVENTS_TOTAL,
    RECOMMENDATION_LATENCY,
    RECOMMENDATION_REQUESTS,
    SEARCH_LATENCY,
    SEARCH_REQUESTS,
)
from app.schemas import EventRequest, JobOut, RecommendationOut, SearchRequest, VariantStatsOut
from app.services import get_recommender, get_session

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_session)) -> list[Job]:
    return db.query(Job).order_by(Job.id).all()


@router.get("/users/{user_id}/recommendations", response_model=list[RecommendationOut])
def recommend(
    user_id: int,
    top_k: Annotated[int, Query(ge=1, le=50)] = 10,
    db: Session = Depends(get_session),
    recommender=Depends(get_recommender),
) -> list[RecommendationOut]:
    user = db.get(UserProfile, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user = ensure_user_variant(db, user)
    start = time.perf_counter()
    recommendations = recommender.recommend(db, user, top_k=top_k)
    RECOMMENDATION_LATENCY.labels(variant=user.ab_variant).observe(time.perf_counter() - start)
    RECOMMENDATION_REQUESTS.labels(variant=user.ab_variant).inc()

    response: list[RecommendationOut] = []
    for position, rec in enumerate(recommendations, start=1):
        job = db.get(Job, rec.job_id)
        if job is None:
            continue
        record_event(
            db,
            user_id=user.id,
            job_id=job.id,
            event_type="impression",
            ab_variant=user.ab_variant,
            position=position,
            score=rec.score,
        )
        EVENTS_TOTAL.labels(event_type="impression", variant=user.ab_variant).inc()
        response.append(
            RecommendationOut(
                job=JobOut.model_validate(job),
                score=rec.score,
                strategy=rec.strategy,
                position=position,
            )
        )
    return response


@router.post("/search", response_model=list[RecommendationOut])
def search(
    payload: SearchRequest,
    db: Session = Depends(get_session),
    recommender=Depends(get_recommender),
) -> list[RecommendationOut]:
    start = time.perf_counter()
    matches = recommender.search(db, payload.query, top_k=payload.top_k)
    SEARCH_LATENCY.observe(time.perf_counter() - start)
    SEARCH_REQUESTS.inc()

    response: list[RecommendationOut] = []
    for position, rec in enumerate(matches, start=1):
        job = db.get(Job, rec.job_id)
        if job is None:
            continue
        response.append(
            RecommendationOut(
                job=JobOut.model_validate(job),
                score=rec.score,
                strategy=rec.strategy,
                position=position,
            )
        )
    return response


@router.post("/events")
def track_event(payload: EventRequest, db: Session = Depends(get_session)) -> dict[str, str]:
    user = db.get(UserProfile, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    job = db.get(Job, payload.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    user = ensure_user_variant(db, user)
    record_event(
        db,
        user_id=user.id,
        job_id=job.id,
        event_type=payload.event_type,
        ab_variant=user.ab_variant,
        position=payload.position,
        score=payload.score,
    )
    EVENTS_TOTAL.labels(event_type=payload.event_type, variant=user.ab_variant).inc()
    return {"status": "recorded"}


@router.get("/ab/stats", response_model=list[VariantStatsOut])
def ab_stats(db: Session = Depends(get_session)) -> list[VariantStatsOut]:
    return [VariantStatsOut.model_validate(item) for item in compute_ab_stats(db)]


@router.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type="text/plain; version=0.0.4")
