from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.auth.database import get_db
from api.auth.service import create_user, get_user_by_email, verify_password, create_access_token
from api.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from api.auth.models import PlanTier

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    user = await create_user(db, body.email, body.password, body.full_name or "", body.company or "")
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        plan=user.plan,
    )

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended")
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        plan=user.plan,
    )
