from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ThreatLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Shield ID models
class DeepfakeImageRequest(BaseModel):
    image_base64: str
    context: Optional[str] = None

class DeepfakeAudioRequest(BaseModel):
    audio_base64: str
    duration_seconds: Optional[float] = None

class DocumentVerifyRequest(BaseModel):
    document_base64: str
    document_type: Optional[str] = "id_card"

class ShieldIDResult(BaseModel):
    is_synthetic: bool
    confidence: float
    threat_level: ThreatLevel
    signals: list[str]
    recommendation: str
    scan_id: str

# Shield Phish models
class PhishEmailRequest(BaseModel):
    subject: str
    body: str
    sender: str
    headers: Optional[dict] = {}

class PhishURLRequest(BaseModel):
    url: str
    context: Optional[str] = None

class ShieldPhishResult(BaseModel):
    is_phishing: bool
    confidence: float
    threat_level: ThreatLevel
    attack_type: Optional[str]
    signals: list[str]
    recommendation: str
    scan_id: str

# Shield Dev models
class CodeScanRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = None

class ShieldDevResult(BaseModel):
    vulnerabilities: list[dict]
    secrets_found: list[dict]
    risk_score: float
    threat_level: ThreatLevel
    fix_suggestions: list[str]
    scan_id: str

# Shield SOC models
class LogAnalysisRequest(BaseModel):
    logs: list[str]
    source: Optional[str] = "system"
    timeframe_minutes: Optional[int] = 60

class ShieldSOCResult(BaseModel):
    anomalies: list[dict]
    threat_level: ThreatLevel
    incident_summary: str
    affected_assets: list[str]
    recommended_actions: list[str]
    auto_remediated: bool
    scan_id: str
