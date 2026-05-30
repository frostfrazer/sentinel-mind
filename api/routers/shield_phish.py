from fastapi import APIRouter, Depends
from api.models.schemas import PhishEmailRequest, PhishURLRequest, ShieldPhishResult
from api.services import shield_phish_service
from api.core.auth import verify_api_key

router = APIRouter()

@router.post("/scan/email", response_model=ShieldPhishResult)
async def scan_email(request: PhishEmailRequest, api_key: str = Depends(verify_api_key)):
    """Detect phishing, BEC, and social engineering in emails."""
    return await shield_phish_service.analyze_email(
        request.subject, request.body, request.sender, request.headers or {}
    )

@router.post("/scan/url", response_model=ShieldPhishResult)
async def scan_url(request: PhishURLRequest, api_key: str = Depends(verify_api_key)):
    """Analyze a URL for phishing or malicious intent."""
    return await shield_phish_service.analyze_url(request.url, request.context or "")

@router.get("/ping")
def ping():
    return {"pillar": "shield-phish", "status": "online"}
