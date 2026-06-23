import numpy as np

from app.recommender import assign_ab_group


def test_ab_group_stable():
    assert assign_ab_group(7) == assign_ab_group(7)


def test_ab_has_both_groups():
    groups = {assign_ab_group(i) for i in range(50)}
    assert "control" in groups
    assert "treatment" in groups
