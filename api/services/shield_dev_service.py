import uuid
import anthropic
from api.core.config import settings
from api.models.schemas import ShieldDevResult, ThreatLevel

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

async def scan_code(code: str, language: str, filename: str = "") -> ShieldDevResult:
    prompt = f"""You are a security code review AI. Analyze this {language} code for vulnerabilities.

Filename: {filename or 'unknown'}
Code:
```{language}
{code[:4000]}
```

Check for:
- OWASP Top 10 vulnerabilities (SQLi, XSS, IDOR, etc.)
- Hardcoded secrets, API keys, passwords, tokens
- Insecure cryptography or random number generation
- Path traversal, command injection
- Insecure deserialization
- Missing authentication/authorization checks
- Sensitive data exposure

Respond in JSON only:
{{
  "vulnerabilities": [{{"type": "string", "severity": "critical|high|medium|low", "line": int_or_null, "description": "string", "fix": "string"}}],
  "secrets_found": [{{"type": "string", "line": int_or_null, "masked_value": "string"}}],
  "risk_score": 0.0-10.0,
  "fix_suggestions": ["top 3 immediate fixes"]
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        import json, re
        text = response.content[0].text
        data = json.loads(re.search(r'\{.*\}', text, re.DOTALL).group())
        risk = float(data.get("risk_score", 0))
        if risk >= 8: tl = ThreatLevel.CRITICAL
        elif risk >= 6: tl = ThreatLevel.HIGH
        elif risk >= 4: tl = ThreatLevel.MEDIUM
        elif risk >= 2: tl = ThreatLevel.LOW
        else: tl = ThreatLevel.SAFE
        return ShieldDevResult(
            vulnerabilities=data.get("vulnerabilities", []),
            secrets_found=data.get("secrets_found", []),
            risk_score=risk,
            threat_level=tl,
            fix_suggestions=data.get("fix_suggestions", []),
            scan_id=str(uuid.uuid4())
        )
    except Exception as e:
        return ShieldDevResult(
            vulnerabilities=[], secrets_found=[], risk_score=0.0,
            threat_level=ThreatLevel.SAFE, fix_suggestions=[str(e)],
            scan_id=str(uuid.uuid4())
        )
