from fastapi import APIRouter, Depends
from api.models.schemas import DeepfakeImageRequest, DocumentVerifyRequest, ShieldIDResult
from api.services import shield_id_service
from api.core.auth import verify_api_key

router = APIRouter()

@router.post("/scan/image", response_model=ShieldIDResult)
async def scan_image(request: DeepfakeImageRequest, api_key: str = Depends(verify_api_key)):
    """Detect AI-generated or deepfake faces in an image."""
    return await shield_id_service.analyze_image(request.image_base64, request.context or "")

@router.post("/scan/document", response_model=ShieldIDResult)
async def scan_document(request: DocumentVerifyRequest, api_key: str = Depends(verify_api_key)):
    """Detect forged or AI-generated identity documents."""
    return await shield_id_service.analyze_document(request.document_base64, request.document_type or "id_card")

@router.get("/ping")
def ping():
    return {"pillar": "shield-id", "status": "online"}
