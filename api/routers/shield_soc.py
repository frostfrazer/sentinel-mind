import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.schemas import LogAnalysisRequest, ShieldSOCResult
from api.services import shield_soc_service
from api.core.auth import verify_api_key, ScanContext
from api.auth.database import get_db
from api.auth.service import log_scan

router = APIRouter()

@router.post("/analyze/logs", response_model=ShieldSOCResult)
async def analyze_logs(
    request: LogAnalysisRequest,
    ctx: ScanContext = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Analyze system/network logs for threats and anomalies."""
    start = time.monotonic()
    result = await shield_soc_service.analyze_logs(
        request.logs, request.source or "system", request.timeframe_minutes or 60
    )
    await log_scan(
        db, ctx.user.id, "shield_soc", "analyze/logs",
        result.threat_level.value, 0.0,
        int((time.monotonic() - start) * 1000),
    )
    return result

@router.get("/ping")
def ping():
    return {"pillar": "shield-soc", "status": "online"}
