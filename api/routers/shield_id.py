import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.schemas import DeepfakeImageRequest, DocumentVerifyRequest, ShieldIDResult
from api.services import shield_id_service
from api.core.auth import verify_api_key, ScanContext
from api.auth.database import get_db
from api.auth.service import log_scan

router = APIRouter()

@router.post("/scan/image", response_model=ShieldIDResult)
async def scan_image(
    request: DeepfakeImageRequest,
    ctx: ScanContext = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Detect AI-generated or deepfake faces in an image."""
    start = time.monotonic()
    result = await shield_id_service.analyze_image(request.image_base64, request.context or "")
    await log_scan(
        db, ctx.user.id, "shield_id", "scan/image",
        result.threat_level.value, result.confidence,
        int((time.monotonic() - start) * 1000),
    )
    return result

@router.post("/scan/document", response_model=ShieldIDResult)
async def scan_document(
    request: DocumentVerifyRequest,
    ctx: ScanContext = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Detect forged or AI-generated identity documents."""
    start = time.monotonic()
    result = await shield_id_service.analyze_document(request.document_base64, request.document_type or "id_card")
    await log_scan(
        db, ctx.user.id, "shield_id", "scan/document",
        result.threat_level.value, result.confidence,
        int((time.monotonic() - start) * 1000),
    )
    return result

@router.get("/ping")
def ping():
    return {"pillar": "shield-id", "status": "online"}
