from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sqlalchemy.orm import Session

from app.db.models import AbVariant, Job, UserProfile
from app.ml.embedder import JobEmbedder
from app.ml.index import FaissIndex


@dataclass
class Recommendation:
    job_id: int
    score: float
    strategy: str


class RecommenderService:
    def __init__(self, embedder: JobEmbedder, index: FaissIndex) -> None:
        self.embedder = embedder
        self.index = index

    def popularity_recommendations(self, db: Session, top_k: int = 10) -> list[Recommendation]:
        jobs = (
            db.query(Job)
            .order_by(Job.applications.desc(), Job.views.desc(), Job.id.asc())
            .limit(top_k)
            .all()
        )
        max_apps = max((job.applications for job in jobs), default=1) or 1
        return [
            Recommendation(
                job_id=job.id,
                score=job.applications / max_apps,
                strategy=AbVariant.CONTROL.value,
            )
            for job in jobs
        ]

    def semantic_recommendations(
        self,
        db: Session,
        user: UserProfile,
        top_k: int = 10,
    ) -> list[Recommendation]:
        profile_text = f"{user.resume_text} Навыки: {user.skills}"
        query_vector = self.embedder.encode_one(profile_text)
        matches = self.index.search(query_vector, top_k=top_k * 2)

        seen: set[int] = set()
        recommendations: list[Recommendation] = []
        for job_id, score in matches:
            if job_id in seen:
                continue
            job = db.get(Job, job_id)
            if job is None:
                continue
            seen.add(job_id)
            recommendations.append(
                Recommendation(job_id=job_id, score=score, strategy=AbVariant.TREATMENT.value)
            )
            if len(recommendations) >= top_k:
                break
        return recommendations

    def recommend(
        self,
        db: Session,
        user: UserProfile,
        top_k: int = 10,
    ) -> list[Recommendation]:
        if user.ab_variant == AbVariant.TREATMENT.value:
            return self.semantic_recommendations(db, user, top_k=top_k)
        return self.popularity_recommendations(db, top_k=top_k)

    def search(self, db: Session, query: str, top_k: int = 10) -> list[Recommendation]:
        query_vector = self.embedder.encode_one(query)
        matches = self.index.search(query_vector, top_k=top_k)
        return [
            Recommendation(job_id=job_id, score=score, strategy="semantic_search")
            for job_id, score in matches
            if db.get(Job, job_id) is not None
        ]
