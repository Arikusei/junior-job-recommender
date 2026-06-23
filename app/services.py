from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.db.models import SessionLocal, init_db
from app.ml.embedder import JobEmbedder, load_embeddings
from app.ml.index import FaissIndex, default_index_path
from app.ml.recommender import RecommenderService


class AppState:
    def __init__(self) -> None:
        self.embedder = JobEmbedder()
        self.index: FaissIndex | None = None
        self.recommender: RecommenderService | None = None

    def load(self) -> None:
        init_db()
        index_path = default_index_path()
        embeddings_path = Path(settings.artifacts_dir) / "job_embeddings.npz"

        if not index_path.with_suffix(".faiss").exists():
            raise FileNotFoundError(
                "FAISS index not found. Run: python scripts/build_index.py"
            )
        if not embeddings_path.exists():
            raise FileNotFoundError(
                "Embeddings not found. Run: python scripts/build_index.py"
            )

        vectors, _ = load_embeddings(embeddings_path)
        self.index = FaissIndex.load(index_path, dimension=vectors.shape[1])
        self.recommender = RecommenderService(self.embedder, self.index)


app_state = AppState()


def get_recommender() -> RecommenderService:
    if app_state.recommender is None:
        raise RuntimeError("Recommender is not initialized")
    return app_state.recommender


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
