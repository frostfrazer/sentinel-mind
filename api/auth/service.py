import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from api.auth.models import User, APIKey, ScanLog, PlanTier
from api.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = settings.API_KEY_SECRET
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

PLAN_LIMITS = {
    PlanTier.FREE:       {"daily": 50,   "monthly": 500},
    PlanTier.STARTER:    {"daily": 500,  "monthly": 10_000},
    PlanTier.PRO:        {"daily": 5000, "monthly": 100_000},
    PlanTier.ENTERPRISE: {"daily": -1,   "monthly": -1},   # unlimited
}

# ── passwords ──────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ── JWT ────────────────────────────────────────────────────────────────────
def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# ── API keys ───────────────────────────────────────────────────────────────
def generate_api_key() -> tuple[str, str, str]:
    """Returns (raw_key, key_hash, key_prefix)"""
    raw = "sm_live_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    prefix = raw[:16] + "..."
    return raw, key_hash, prefix

async def hash_and_store_key(db: AsyncSession, user_id: str, name: str) -> str:
    raw, key_hash, prefix = generate_api_key()
    key = APIKey(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=name,
        key_hash=key_hash,
        key_prefix=prefix,
    )
    db.add(key)
    await db.commit()
    return raw   # shown ONCE to user — never stored again

async def verify_api_key_db(db: AsyncSession, raw_key: str) -> Optional[APIKey]:
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    result = await db.execute(select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True))
    api_key = result.scalar_one_or_none()
    if api_key:
        await db.execute(
            update(APIKey).where(APIKey.id == api_key.id)
            .values(last_used=datetime.now(timezone.utc), scans_total=APIKey.scans_total + 1)
        )
        await db.commit()
    return api_key

# ── users ──────────────────────────────────────────────────────────────────
async def create_user(db: AsyncSession, email: str, password: str, full_name: str = "", company: str = "") -> User:
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        company=company,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# ── scan logging ───────────────────────────────────────────────────────────
async def log_scan(db: AsyncSession, user_id: str, pillar: str, endpoint: str,
                   threat_level: str, confidence: float = 0.0, duration_ms: int = 0):
    log = ScanLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        pillar=pillar,
        endpoint=endpoint,
        threat_level=threat_level,
        confidence=confidence,
        duration_ms=duration_ms,
    )
    db.add(log)
    await db.commit()
