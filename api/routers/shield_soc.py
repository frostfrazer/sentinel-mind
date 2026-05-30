from fastapi import APIRouter, Depends
from api.models.schemas import LogAnalysisRequest, ShieldSOCResult
from api.services import shield_soc_service
from api.core.auth import verify_api_key

router = APIRouter()

@router.post("/analyze/logs", response_model=ShieldSOCResult)
async def analyze_logs(request: LogAnalysisRequest, api_key: str = Depends(verify_api_key)):
    """Analyze system/network logs for threats and anomalies."""
    return await shield_soc_service.analyze_logs(
        request.logs, request.source or "system", request.timeframe_minutes or 60
    )

@router.get("/ping")
def ping():
    return {"pillar": "shield-soc", "status": "online"}
