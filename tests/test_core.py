import numpy as np

from app.ab.experiment import assign_variant
from app.db.models import AbVariant
from app.ml.embedder import JobEmbedder
from app.ml.index import FaissIndex


def test_assign_variant_is_deterministic():
    assert assign_variant(42) == assign_variant(42)


def test_assign_variant_splits_users():
    variants = {assign_variant(user_id) for user_id in range(1, 101)}
    assert AbVariant.CONTROL in variants
    assert AbVariant.TREATMENT in variants


def test_faiss_search_returns_neighbors():
    vectors = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )
    index = FaissIndex(dimension=3)
    index.build(vectors, job_ids=[1, 2, 3])

    results = index.search(np.array([1.0, 0.0, 0.0], dtype=np.float32), top_k=2)
    assert results[0][0] == 1
    assert results[1][0] == 2


def test_embedder_job_text_format():
    embedder = JobEmbedder()
    text = embedder.job_text("Junior Python", "API development", "Python, SQL")
    assert "Junior Python" in text
    assert "Python, SQL" in text
