import pytest
import httpx
from api.main import app
from api.auth.database import init_db, AsyncSessionLocal
from api.auth.service import create_user, hash_and_store_key

BASE = "http://localhost:8000"


@pytest.fixture(scope="session", autouse=True)
async def _init_test_db():
    await init_db()


@pytest.fixture
async def auth_headers():
    """Creates a real user + API key in the test DB and returns auth headers."""
    async with AsyncSessionLocal() as db:
        import uuid
        email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        user = await create_user(db, email=email, password="testpass123", full_name="Test User")
        raw_key = await hash_and_store_key(db, user.id, "test-key")
    return {"X-API-Key": raw_key}

@pytest.mark.asyncio
async def test_root():
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.get("/")
        assert r.status_code == 200
        assert r.json()["name"] == "SentinelMind"

@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_shield_id_ping():
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.get("/v1/shield-id/ping")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_shield_phish_ping():
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.get("/v1/shield-phish/ping")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_shield_dev_ping():
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.get("/v1/shield-dev/ping")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_shield_soc_ping():
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.get("/v1/shield-soc/ping")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_phish_url_scan(auth_headers):
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.post(
            "/v1/shield-phish/scan/url",
            json={"url": "http://paypa1-secure-login.xyz/verify"},
            headers=auth_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert "is_phishing" in data
        assert "confidence" in data
        assert "threat_level" in data

@pytest.mark.asyncio
async def test_dev_code_scan(auth_headers):
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.post(
            "/v1/shield-dev/scan/code",
            json={
                "code": "password = 'admin123'\nquery = f'SELECT * FROM users WHERE id={user_input}'",
                "language": "python",
                "filename": "auth.py"
            },
            headers=auth_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert "vulnerabilities" in data
        assert "risk_score" in data

@pytest.mark.asyncio
async def test_soc_log_analysis(auth_headers):
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.post(
            "/v1/shield-soc/analyze/logs",
            json={
                "logs": [
                    "2026-05-29 02:13:41 FAILED LOGIN user=admin ip=185.220.101.45",
                    "2026-05-29 02:13:42 FAILED LOGIN user=admin ip=185.220.101.45",
                    "2026-05-29 02:13:43 FAILED LOGIN user=root ip=185.220.101.45",
                    "2026-05-29 02:13:44 SUCCESS LOGIN user=admin ip=185.220.101.45",
                ],
                "source": "auth_logs",
                "timeframe_minutes": 5
            },
            headers=auth_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert "incident_summary" in data
        assert "recommended_actions" in data
