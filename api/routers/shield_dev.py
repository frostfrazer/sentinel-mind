import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.schemas import CodeScanRequest, ShieldDevResult
from api.services import shield_dev_service
from api.core.auth import verify_api_key, ScanContext
from api.auth.database import get_db
from api.auth.service import log_scan

router = APIRouter()

@router.post("/scan/code", response_model=ShieldDevResult)
async def scan_code(
    request: CodeScanRequest,
    ctx: ScanContext = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Scan code for vulnerabilities, secrets, and security issues."""
    start = time.monotonic()
    result = await shield_dev_service.scan_code(
        request.code, request.language, request.filename or ""
    )
    await log_scan(
        db, ctx.user.id, "shield_dev", "scan/code",
        result.threat_level.value, result.risk_score / 10.0,
        int((time.monotonic() - start) * 1000),
    )
    return result

@router.get("/ping")
def ping():
    return {"pillar": "shield-dev", "status": "online"}
