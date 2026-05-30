import uuid
import anthropic
from api.core.config import settings
from api.models.schemas import ShieldPhishResult, ThreatLevel

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

async def analyze_email(subject: str, body: str, sender: str, headers: dict) -> ShieldPhishResult:
    prompt = f"""You are a phishing detection AI. Analyze this email for social engineering attacks.

Sender: {sender}
Subject: {subject}
Headers: {headers}
Body:
{body[:3000]}

Check for:
- Urgency manipulation, fear tactics, impersonation
- Suspicious sender domain spoofing
- Credential harvesting attempts
- Business email compromise (BEC) patterns
- Known phishing template matches

Respond in JSON only:
{{"is_phishing": bool, "confidence": 0.0-1.0, "attack_type": "string or null", "signals": ["specific indicators"], "recommendation": "action for recipient"}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        import json, re
        text = response.content[0].text
        data = json.loads(re.search(r'\{.*\}', text, re.DOTALL).group())
        confidence = float(data.get("confidence", 0.5))
        is_phish = data.get("is_phishing", False)
        tl = ThreatLevel.SAFE
        if is_phish:
            if confidence > 0.9: tl = ThreatLevel.CRITICAL
            elif confidence > 0.7: tl = ThreatLevel.HIGH
            elif confidence > 0.5: tl = ThreatLevel.MEDIUM
            else: tl = ThreatLevel.LOW
        return ShieldPhishResult(
            is_phishing=is_phish,
            confidence=confidence,
            threat_level=tl,
            attack_type=data.get("attack_type"),
            signals=data.get("signals", []),
            recommendation=data.get("recommendation", "Exercise caution"),
            scan_id=str(uuid.uuid4())
        )
    except Exception as e:
        return ShieldPhishResult(
            is_phishing=False, confidence=0.0, threat_level=ThreatLevel.SAFE,
            attack_type=None, signals=[str(e)],
            recommendation="Manual review", scan_id=str(uuid.uuid4())
        )

async def analyze_url(url: str, context: str = "") -> ShieldPhishResult:
    prompt = f"""You are a URL threat intelligence AI. Analyze this URL for phishing/malware:

URL: {url}
Context: {context or "User clicked link"}

Check for:
- Typosquatting of known brands
- Suspicious TLD or subdomain patterns
- URL shortener obfuscation
- Known malicious domain patterns
- Punycode/homograph attacks

Respond in JSON only:
{{"is_phishing": bool, "confidence": 0.0-1.0, "attack_type": "string or null", "signals": ["indicators"], "recommendation": "action"}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        import json, re
        text = response.content[0].text
        data = json.loads(re.search(r'\{.*\}', text, re.DOTALL).group())
        confidence = float(data.get("confidence", 0.5))
        is_phish = data.get("is_phishing", False)
        tl_map = {True: ThreatLevel.HIGH, False: ThreatLevel.SAFE}
        return ShieldPhishResult(
            is_phishing=is_phish, confidence=confidence,
            threat_level=ThreatLevel.HIGH if (is_phish and confidence > 0.7) else ThreatLevel.SAFE,
            attack_type=data.get("attack_type"), signals=data.get("signals", []),
            recommendation=data.get("recommendation", "Do not visit"),
            scan_id=str(uuid.uuid4())
        )
    except Exception as e:
        return ShieldPhishResult(
            is_phishing=False, confidence=0.0, threat_level=ThreatLevel.SAFE,
            attack_type=None, signals=[str(e)],
            recommendation="Manual review", scan_id=str(uuid.uuid4())
        )
