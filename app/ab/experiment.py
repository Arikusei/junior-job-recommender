from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import AbVariant, UserProfile


def assign_variant(user_id: int, control_ratio: float | None = None) -> AbVariant:
    ratio = control_ratio if control_ratio is not None else settings.ab_control_ratio
    digest = hashlib.md5(str(user_id).encode()).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    return AbVariant.CONTROL if bucket < ratio else AbVariant.TREATMENT


def ensure_user_variant(db: Session, user: UserProfile) -> UserProfile:
    if not user.ab_variant:
        user.ab_variant = assign_variant(user.id).value
        db.commit()
        db.refresh(user)
    return user
