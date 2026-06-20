import uuid
import base64
import anthropic
from api.core.config import settings
from api.models.schemas import ShieldIDResult, ThreatLevel

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def _threat_from_confidence(confidence: float) -> ThreatLevel:
    if confidence < 0.3: return ThreatLevel.SAFE
    if confidence < 0.5: return ThreatLevel.LOW
    if confidence < 0.7: return ThreatLevel.MEDIUM
    if confidence < 0.9: return ThreatLevel.HIGH
    return ThreatLevel.CRITICAL

async def analyze_image(image_base64: str, context: str = "") -> ShieldIDResult:
    prompt = f"""You are a deepfake detection AI. Analyze this image for signs of:
- GAN artifacts (unnatural skin texture, hair, backgrounds)
- Face swap indicators (boundary artifacts, lighting inconsistencies)
- AI-generated facial features

Context: {context or 'Identity verification request'}

Respond in JSON only:
{{"is_synthetic": bool, "confidence": 0.0-1.0, "signals": ["list of specific indicators found"], "recommendation": "one sentence action"}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_base64}},
                    {"type": "text", "text": prompt}
                ]
            }]
        )
        import json, re
        text = response.content[0].text
        data = json.loads(re.search(r'\{.*\}', text, re.DOTALL).group())
        confidence = float(data.get("confidence", 0.5))
        return ShieldIDResult(
            is_synthetic=data.get("is_synthetic", False),
            confidence=confidence,
            threat_level=_threat_from_confidence(confidence if data.get("is_synthetic") else 0),
            signals=data.get("signals", []),
            recommendation=data.get("recommendation", "Manual review recommended"),
            scan_id=str(uuid.uuid4())
        )
    except Exception as e:
        return ShieldIDResult(
            is_synthetic=False, confidence=0.0,
            threat_level=ThreatLevel.SAFE, signals=[f"Analysis error: {str(e)}"],
            recommendation="Retry or escalate to manual review",
            scan_id=str(uuid.uuid4())
        )

async def analyze_document(document_base64: str, doc_type: str = "id_card") -> ShieldIDResult:
    prompt = f"""You are a document forgery detection AI. Analyze this {doc_type} for:
- Font inconsistencies or digital manipulation
- Security feature anomalies (holograms, watermarks)
- Metadata tampering signs
- Template mismatch vs known authentic documents

Respond in JSON only:
{{"is_synthetic": bool, "confidence": 0.0-1.0, "signals": ["specific forgery indicators"], "recommendation": "action"}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": document_base64}},
                    {"type": "text", "text": prompt}
                ]
            }]
        )
        import json, re
        text = response.content[0].text
        data = json.loads(re.search(r'\{.*\}', text, re.DOTALL).group())
        confidence = float(data.get("confidence", 0.5))
        return ShieldIDResult(
            is_synthetic=data.get("is_synthetic", False),
            confidence=confidence,
            threat_level=_threat_from_confidence(confidence if data.get("is_synthetic") else 0),
            signals=data.get("signals", []),
            recommendation=data.get("recommendation", "Manual review recommended"),
            scan_id=str(uuid.uuid4())
        )
    except Exception as e:
        return ShieldIDResult(
            is_synthetic=False, confidence=0.0,
            threat_level=ThreatLevel.SAFE, signals=[str(e)],
            recommendation="Retry scan", scan_id=str(uuid.uuid4())
        )
