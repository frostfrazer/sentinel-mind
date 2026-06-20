from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.auth.database import get_db
from api.auth.service import verify_api_key_db, PLAN_LIMITS
from api.auth.models import APIKey, User, ScanLog

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@dataclass
class ScanContext:
    """Bundled identity for an authenticated, rate-limited scan request."""
    api_key: APIKey
    user: User


async def verify_api_key(
    raw_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> ScanContext:
    """
    Real auth + usage-limit gate for all Shield pillar endpoints.

    Replaces the old stub that always 403'd in production. Looks the key up
    in the DB (hashed comparison), resolves the owning user, then enforces
    that user's plan-tier daily/monthly scan limits before letting the
    request through.
    """
    if not raw_key:
        raise HTTPException(status_code=401, detail="X-API-Key header required")

    api_key = await verify_api_key_db(db, raw_key)
    if not api_key:
        raise HTTPException(status_code=403, detail="Invalid or revoked API key")

    result = await db.execute(select(User).where(User.id == api_key.user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Account inactive or not found")

    limits = PLAN_LIMITS[user.plan]
    daily_limit = limits["daily"]
    monthly_limit = limits["monthly"]

    if daily_limit != -1 or monthly_limit != -1:
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if daily_limit != -1:
            daily_count = await db.scalar(
                select(func.count(ScanLog.id)).where(
                    ScanLog.user_id == user.id, ScanLog.created_at >= day_start
                )
            )
            if daily_count >= daily_limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Daily scan limit reached ({daily_limit}/day on {user.plan.value} plan). Upgrade your plan or try again tomorrow.",
                )

        if monthly_limit != -1:
            monthly_count = await db.scalar(
                select(func.count(ScanLog.id)).where(
                    ScanLog.user_id == user.id, ScanLog.created_at >= month_start
                )
            )
            if monthly_count >= monthly_limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Monthly scan limit reached ({monthly_limit}/month on {user.plan.value} plan). Upgrade your plan.",
                )

    return ScanContext(api_key=api_key, user=user)
