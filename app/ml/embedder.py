from __future__ import annotations

from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings


class JobEmbedder:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.embedding_model
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def job_text(self, title: str, description: str, skills: str) -> str:
        return f"{title}. {description} Навыки: {skills}"

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32)

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]


def save_embeddings(path: Path, vectors: np.ndarray, job_ids: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, vectors=vectors, job_ids=np.array(job_ids, dtype=np.int32))


def load_embeddings(path: Path) -> tuple[np.ndarray, list[int]]:
    data = np.load(path)
    return data["vectors"], data["job_ids"].tolist()
