import uuid
import anthropic
from fastapi import HTTPException
from api.core.config import settings
from api.models.schemas import ShieldSOCResult, ThreatLevel

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

async def analyze_logs(logs: list, source: str, timeframe_minutes: int) -> ShieldSOCResult:
    log_sample = "\n".join(logs[:100])
    prompt = f"""You are an autonomous SOC analyst AI. Analyze these {source} logs from the last {timeframe_minutes} minutes.

Logs:
{log_sample}

Detect:
- Brute force / credential stuffing attacks
- Lateral movement patterns
- Data exfiltration indicators
- Privilege escalation attempts
- Unusual process execution or network connections
- Known attack TTPs (MITRE ATT&CK)

Respond in JSON only:
{{
  "anomalies": [{{"type": "string", "severity": "critical|high|medium|low", "description": "string", "timestamp": "string_or_null", "raw_indicator": "string"}}],
  "threat_level": "safe|low|medium|high|critical",
  "incident_summary": "2-3 sentence plain English summary",
  "affected_assets": ["list of IPs/hostnames/users involved"],
  "recommended_actions": ["ordered list of immediate actions"],
  "auto_remediated": false
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
        tl_map = {
            "safe": ThreatLevel.SAFE, "low": ThreatLevel.LOW,
            "medium": ThreatLevel.MEDIUM, "high": ThreatLevel.HIGH,
            "critical": ThreatLevel.CRITICAL
        }
        return ShieldSOCResult(
            anomalies=data.get("anomalies", []),
            threat_level=tl_map.get(data.get("threat_level", "safe"), ThreatLevel.SAFE),
            incident_summary=data.get("incident_summary", "No significant threats detected"),
            affected_assets=data.get("affected_assets", []),
            recommended_actions=data.get("recommended_actions", []),
            auto_remediated=data.get("auto_remediated", False),
            scan_id=str(uuid.uuid4())
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scan engine unavailable: {str(e)}")
