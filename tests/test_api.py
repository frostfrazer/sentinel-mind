import pytest
import httpx
from api.main import app

BASE = "http://localhost:8000"
HEADERS = {"X-API-Key": "dev-test-key"}

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
async def test_phish_url_scan():
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.post(
            "/v1/shield-phish/scan/url",
            json={"url": "http://paypa1-secure-login.xyz/verify"},
            headers=HEADERS
        )
        assert r.status_code == 200
        data = r.json()
        assert "is_phishing" in data
        assert "confidence" in data
        assert "threat_level" in data

@pytest.mark.asyncio
async def test_dev_code_scan():
    async with httpx.AsyncClient(app=app, base_url=BASE) as client:
        r = await client.post(
            "/v1/shield-dev/scan/code",
            json={
                "code": "password = 'admin123'\nquery = f'SELECT * FROM users WHERE id={user_input}'",
                "language": "python",
                "filename": "auth.py"
            },
            headers=HEADERS
        )
        assert r.status_code == 200
        data = r.json()
        assert "vulnerabilities" in data
        assert "risk_score" in data

@pytest.mark.asyncio
async def test_soc_log_analysis():
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
            headers=HEADERS
        )
        assert r.status_code == 200
        data = r.json()
        assert "incident_summary" in data
        assert "recommended_actions" in data
