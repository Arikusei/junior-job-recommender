from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np

from app.config import settings


class FaissIndex:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.job_ids: list[int] = []

    def build(self, vectors: np.ndarray, job_ids: list[int]) -> None:
        if vectors.shape[0] != len(job_ids):
            raise ValueError("vectors and job_ids length mismatch")
        self.job_ids = list(job_ids)
        self.index.reset()
        self.index.add(vectors)

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> list[tuple[int, float]]:
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        scores, indices = self.index.search(query_vector.astype(np.float32), top_k)
        results: list[tuple[int, float]] = []
        for idx, score in zip(indices[0], scores[0], strict=True):
            if idx < 0:
                continue
            results.append((self.job_ids[idx], float(score)))
        return results

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path.with_suffix(".faiss")))
        np.save(path.with_suffix(".ids.npy"), np.array(self.job_ids, dtype=np.int32))

    @classmethod
    def load(cls, path: Path, dimension: int) -> FaissIndex:
        instance = cls(dimension)
        instance.index = faiss.read_index(str(path.with_suffix(".faiss")))
        instance.job_ids = np.load(path.with_suffix(".ids.npy")).tolist()
        return instance


def default_index_path() -> Path:
    return Path(settings.artifacts_dir) / "job_index"
