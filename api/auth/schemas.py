from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from api.auth.models import PlanTier

# ── Auth ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = ""
    company: Optional[str] = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    plan: PlanTier

# ── Users ──────────────────────────────────────────────────────────────────
class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    company: Optional[str]
    plan: PlanTier
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None

# ── API Keys ───────────────────────────────────────────────────────────────
class CreateAPIKeyRequest(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    is_active: bool
    scans_total: int
    last_used: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class APIKeyCreatedResponse(BaseModel):
    id: str
    name: str
    raw_key: str      # shown ONCE
    key_prefix: str
    message: str = "Store this key securely — it will never be shown again"

# ── Billing ────────────────────────────────────────────────────────────────
class PlanInfo(BaseModel):
    plan: PlanTier
    daily_limit: int
    monthly_limit: int
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]

class CheckoutRequest(BaseModel):
    plan: PlanTier
    success_url: str
    cancel_url: str

class CheckoutResponse(BaseModel):
    checkout_url: str

# ── Usage ──────────────────────────────────────────────────────────────────
class UsageStat(BaseModel):
    pillar: str
    count: int
    last_scan: Optional[datetime]

class UsageResponse(BaseModel):
    total_scans: int
    scans_by_pillar: list[UsageStat]
    plan: PlanTier
    daily_limit: int
