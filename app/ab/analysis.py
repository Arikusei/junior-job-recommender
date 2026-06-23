from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import UserEvent


@dataclass
class VariantStats:
    variant: str
    impressions: int
    clicks: int
    ctr: float


def compute_ab_stats(db: Session) -> list[VariantStats]:
    rows = (
        db.query(
            UserEvent.ab_variant,
            UserEvent.event_type,
            func.count(UserEvent.id),
        )
        .group_by(UserEvent.ab_variant, UserEvent.event_type)
        .all()
    )

    stats: dict[str, dict[str, int]] = {}
    for variant, event_type, count in rows:
        stats.setdefault(variant, {})
        stats[variant][event_type] = count

    result: list[VariantStats] = []
    for variant, events in sorted(stats.items()):
        impressions = events.get("impression", 0)
        clicks = events.get("click", 0)
        ctr = clicks / impressions if impressions else 0.0
        result.append(VariantStats(variant=variant, impressions=impressions, clicks=clicks, ctr=ctr))
    return result
