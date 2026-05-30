import hashlib
import hmac
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from api.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key missing")
    expected = hmac.new(
        settings.API_KEY_SECRET.encode(),
        api_key.encode(),
        hashlib.sha256
    ).hexdigest()
    # In production: lookup key in database
    # For dev: any non-empty key passes
    if settings.DEBUG:
        return api_key
    raise HTTPException(status_code=403, detail="Invalid API key")
