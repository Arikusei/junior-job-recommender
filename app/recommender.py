import hashlib
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.config import ARTIFACTS_DIR, EMBEDDING_MODEL
from app.database import Job, UserProfile

# грузим модель один раз при старте
_model = None
_index = None
_job_ids = []


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def job_to_text(job):
    return f"{job.title}. {job.description} Навыки: {job.skills}"


def encode_texts(texts):
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vectors, dtype=np.float32)


def build_and_save_index(db: Session):
    jobs = db.query(Job).order_by(Job.id).all()
    texts = [job_to_text(j) for j in jobs]
    vectors = encode_texts(texts)
    job_ids = [j.id for j in jobs]

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    out = Path(ARTIFACTS_DIR)
    out.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out / "jobs.faiss"))
    np.save(out / "job_ids.npy", np.array(job_ids))

    return len(jobs)


def load_index():
    global _index, _job_ids
    if _index is not None:
        return

    out = Path(ARTIFACTS_DIR)
    _index = faiss.read_index(str(out / "jobs.faiss"))
    _job_ids = np.load(out / "job_ids.npy").tolist()


def search_similar(query_vec, top_k=10):
    load_index()
    if query_vec.ndim == 1:
        query_vec = query_vec.reshape(1, -1)
    scores, idxs = _index.search(query_vec.astype(np.float32), top_k)
    result = []
    for i, score in zip(idxs[0], scores[0]):
        if i < 0:
            continue
        result.append((_job_ids[i], float(score)))
    return result


def assign_ab_group(user_id: int) -> str:
    # просто делим пополам по хэшу, без лишней магии
    h = int(hashlib.md5(str(user_id).encode()).hexdigest()[:8], 16)
    return "control" if h % 2 == 0 else "treatment"


def recommend_popular(db: Session, top_k=10):
    jobs = db.query(Job).order_by(Job.applications.desc(), Job.views.desc()).limit(top_k).all()
    max_app = max((j.applications for j in jobs), default=1) or 1
    return [(j, j.applications / max_app) for j in jobs]


def recommend_semantic(db: Session, user: UserProfile, top_k=10):
    text = f"{user.resume_text} {user.skills}"
    vec = encode_texts([text])[0]
    matches = search_similar(vec, top_k=top_k)
    out = []
    for job_id, score in matches:
        job = db.get(Job, job_id)
        if job:
            out.append((job, score))
    return out


def recommend_for_user(db: Session, user: UserProfile, top_k=10):
    if user.ab_variant == "treatment":
        return recommend_semantic(db, user, top_k)
    return recommend_popular(db, top_k)


def search_jobs(db: Session, query: str, top_k=10):
    vec = encode_texts([query])[0]
    matches = search_similar(vec, top_k=top_k)
    out = []
    for job_id, score in matches:
        job = db.get(Job, job_id)
        if job:
            out.append((job, score))
    return out


def ab_stats(db: Session):
    from sqlalchemy import func

    from app.database import UserEvent

    rows = (
        db.query(UserEvent.ab_variant, UserEvent.event_type, func.count(UserEvent.id))
        .group_by(UserEvent.ab_variant, UserEvent.event_type)
        .all()
    )
    stats = {}
    for variant, event_type, cnt in rows:
        stats.setdefault(variant, {"impression": 0, "click": 0})
        stats[variant][event_type] = cnt

    result = []
    for variant, data in stats.items():
        imp = data.get("impression", 0)
        clk = data.get("click", 0)
        ctr = clk / imp if imp else 0
        result.append({"variant": variant, "impressions": imp, "clicks": clk, "ctr": round(ctr, 4)})
    return result
