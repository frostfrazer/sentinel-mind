from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from api.auth.database import get_db
from api.auth.dependencies import get_current_user
from api.auth.service import hash_and_store_key
from api.auth.models import User, APIKey
from api.auth.schemas import (
    UserProfile, UpdateProfileRequest,
    CreateAPIKeyRequest, APIKeyResponse, APIKeyCreatedResponse,
    UsageResponse, UsageStat
)
from sqlalchemy import func

router = APIRouter()

@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserProfile)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.company is not None:
        current_user.company = body.company
    await db.commit()
    await db.refresh(current_user)
    return current_user

# ── API Keys ───────────────────────────────────────────────────────────────
@router.post("/api-keys", response_model=APIKeyCreatedResponse, status_code=201)
async def create_api_key(
    body: CreateAPIKeyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Free plan: max 2 keys
    result = await db.execute(select(func.count()).select_from(APIKey).where(APIKey.user_id == current_user.id, APIKey.is_active == True))
    count = result.scalar()
    if current_user.plan.value == "free" and count >= 2:
        raise HTTPException(status_code=403, detail="Free plan allows max 2 API keys. Upgrade to Pro.")
    raw_key = await hash_and_store_key(db, current_user.id, body.name)
    result = await db.execute(select(APIKey).where(APIKey.user_id == current_user.id).order_by(APIKey.created_at.desc()))
    new_key = result.scalars().first()
    return APIKeyCreatedResponse(id=new_key.id, name=new_key.name, raw_key=raw_key, key_prefix=new_key.key_prefix)

@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(APIKey).where(APIKey.user_id == current_user.id).order_by(APIKey.created_at.desc()))
    return result.scalars().all()

@router.delete("/api-keys/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(APIKey).where(APIKey.id == key_id, APIKey.user_id == current_user.id))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = False
    await db.commit()

# ── Usage ──────────────────────────────────────────────────────────────────
@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from api.auth.models import ScanLog
    from api.auth.service import PLAN_LIMITS
    result = await db.execute(
        select(ScanLog.pillar, func.count(ScanLog.id), func.max(ScanLog.created_at))
        .where(ScanLog.user_id == current_user.id)
        .group_by(ScanLog.pillar)
    )
    rows = result.all()
    total = sum(r[1] for r in rows)
    limits = PLAN_LIMITS[current_user.plan]
    return UsageResponse(
        total_scans=total,
        scans_by_pillar=[UsageStat(pillar=r[0], count=r[1], last_scan=r[2]) for r in rows],
        plan=current_user.plan,
        daily_limit=limits["daily"],
    )
