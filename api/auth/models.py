from sqlalchemy import Column, String, Boolean, Integer, DateTime, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, timezone
import enum

class Base(DeclarativeBase):
    pass

class PlanTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = "users"
    id             = Column(String, primary_key=True)
    email          = Column(String, unique=True, nullable=False, index=True)
    hashed_password= Column(String, nullable=False)
    full_name      = Column(String, nullable=True)
    company        = Column(String, nullable=True)
    is_active      = Column(Boolean, default=True)
    is_verified    = Column(Boolean, default=False)
    plan           = Column(SAEnum(PlanTier), default=PlanTier.FREE)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    created_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    api_keys       = relationship("APIKey", back_populates="user", cascade="all, delete")
    scan_logs      = relationship("ScanLog", back_populates="user", cascade="all, delete")

class APIKey(Base):
    __tablename__ = "api_keys"
    id          = Column(String, primary_key=True)
    user_id     = Column(String, ForeignKey("users.id"), nullable=False)
    name        = Column(String, nullable=False)
    key_hash    = Column(String, nullable=False, unique=True)
    key_prefix  = Column(String, nullable=False)        # e.g. "sm_live_xxxx" — shown to user
    is_active   = Column(Boolean, default=True)
    last_used   = Column(DateTime, nullable=True)
    scans_today = Column(Integer, default=0)
    scans_total = Column(Integer, default=0)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at  = Column(DateTime, nullable=True)

    user        = relationship("User", back_populates="api_keys")

class ScanLog(Base):
    __tablename__ = "scan_logs"
    id          = Column(String, primary_key=True)
    user_id     = Column(String, ForeignKey("users.id"), nullable=False)
    pillar      = Column(String, nullable=False)        # shield_id, shield_phish, etc.
    endpoint    = Column(String, nullable=False)
    threat_level= Column(String, nullable=False)
    confidence  = Column(Float, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user        = relationship("User", back_populates="scan_logs")
