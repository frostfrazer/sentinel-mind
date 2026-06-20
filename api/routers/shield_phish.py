import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.schemas import PhishEmailRequest, PhishURLRequest, ShieldPhishResult
from api.services import shield_phish_service
from api.core.auth import verify_api_key, ScanContext
from api.auth.database import get_db
from api.auth.service import log_scan

router = APIRouter()

@router.post("/scan/email", response_model=ShieldPhishResult)
async def scan_email(
    request: PhishEmailRequest,
    ctx: ScanContext = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Detect phishing, BEC, and social engineering in emails."""
    start = time.monotonic()
    result = await shield_phish_service.analyze_email(
        request.subject, request.body, request.sender, request.headers or {}
    )
    await log_scan(
        db, ctx.user.id, "shield_phish", "scan/email",
        result.threat_level.value, result.confidence,
        int((time.monotonic() - start) * 1000),
    )
    return result

@router.post("/scan/url", response_model=ShieldPhishResult)
async def scan_url(
    request: PhishURLRequest,
    ctx: ScanContext = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Analyze a URL for phishing or malicious intent."""
    start = time.monotonic()
    result = await shield_phish_service.analyze_url(request.url, request.context or "")
    await log_scan(
        db, ctx.user.id, "shield_phish", "scan/url",
        result.threat_level.value, result.confidence,
        int((time.monotonic() - start) * 1000),
    )
    return result

@router.get("/ping")
def ping():
    return {"pillar": "shield-phish", "status": "online"}
