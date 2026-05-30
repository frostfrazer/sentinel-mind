from fastapi import APIRouter, Depends
from api.models.schemas import CodeScanRequest, ShieldDevResult
from api.services import shield_dev_service
from api.core.auth import verify_api_key

router = APIRouter()

@router.post("/scan/code", response_model=ShieldDevResult)
async def scan_code(request: CodeScanRequest, api_key: str = Depends(verify_api_key)):
    """Scan code for vulnerabilities, secrets, and security issues."""
    return await shield_dev_service.scan_code(
        request.code, request.language, request.filename or ""
    )

@router.get("/ping")
def ping():
    return {"pillar": "shield-dev", "status": "online"}
