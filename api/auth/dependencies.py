from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from api.auth.database import get_db
from api.auth.service import decode_access_token, get_user_by_id, verify_api_key_db
from api.auth.models import User, APIKey

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

async def require_api_key(
    raw_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> APIKey:
    if not raw_key:
        raise HTTPException(status_code=401, detail="X-API-Key header required")
    api_key = await verify_api_key_db(db, raw_key)
    if not api_key:
        raise HTTPException(status_code=403, detail="Invalid or revoked API key")
    return api_key
