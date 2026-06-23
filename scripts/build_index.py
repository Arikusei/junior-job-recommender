"""Build Sentence-BERT embeddings and FAISS index from job vacancies."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlflow

from app.config import settings
from app.db.models import Job, SessionLocal, init_db
from app.ml.embedder import JobEmbedder, save_embeddings
from app.ml.index import FaissIndex, default_index_path


def build_index() -> None:
    Path(settings.artifacts_dir).mkdir(parents=True, exist_ok=True)
    mlruns_dir = Path("mlruns")
    mlruns_dir.mkdir(exist_ok=True)
    mlflow.set_tracking_uri(f"sqlite:///{(mlruns_dir / 'mlflow.db').resolve().as_posix()}")
    init_db()

    db = SessionLocal()
    try:
        jobs = db.query(Job).order_by(Job.id).all()
        if not jobs:
            raise RuntimeError("No jobs in database. Run: python scripts/seed_data.py")

        embedder = JobEmbedder()
        texts = [embedder.job_text(job.title, job.description, job.skills) for job in jobs]
        job_ids = [job.id for job in jobs]

        with mlflow.start_run(run_name="build_job_index"):
            mlflow.log_param("model", embedder.model_name)
            mlflow.log_param("jobs_count", len(jobs))

            vectors = embedder.encode(texts)
            embeddings_path = Path(settings.artifacts_dir) / "job_embeddings.npz"
            save_embeddings(embeddings_path, vectors, job_ids)

            index = FaissIndex(dimension=vectors.shape[1])
            index.build(vectors, job_ids)
            index.save(default_index_path())

            mlflow.log_artifact(str(embeddings_path))
            mlflow.log_metric("vector_dim", vectors.shape[1])

        print(f"Built index for {len(jobs)} jobs -> {default_index_path()}")
    finally:
        db.close()


if __name__ == "__main__":
    build_index()
