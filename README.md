# SentinelMind

> AI-native cybersecurity platform — identity, threats, code & human layer

---

## Four pillars. One platform.

| Pillar | What it does | Endpoint prefix |
|---|---|---|
| **Shield ID** | Deepfake face, voice & document forgery detection | `/v1/shield-id` |
| **Shield Phish** | Email & URL phishing / social engineering detection | `/v1/shield-phish` |
| **Shield Dev** | Real-time code vulnerability & secret scanning | `/v1/shield-dev` |
| **Shield SOC** | Autonomous log analysis & threat detection | `/v1/shield-soc` |

---

## Quickstart

### 1. Clone & setup
```bash
cd C:\Users\DNjeri\Documents\sentinelmind
copy .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

### 2. Run
```bash
run.bat
```

### 3. Open API docs
```
http://localhost:8000/docs
```

---

## API usage

All endpoints require header: `X-API-Key: your-key`

### Shield ID — Deepfake image scan
```bash
curl -X POST http://localhost:8000/v1/shield-id/scan/image \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "<base64>", "context": "KYC verification"}'
```

### Shield Phish — URL scan
```bash
curl -X POST http://localhost:8000/v1/shield-phish/scan/url \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypa1-secure-login.xyz/verify"}'
```

### Shield Dev — Code scan
```bash
curl -X POST http://localhost:8000/v1/shield-dev/scan/code \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{"code": "query = f\"SELECT * FROM users WHERE id={user_input}\"", "language": "python"}'
```

### Shield SOC — Log analysis
```bash
curl -X POST http://localhost:8000/v1/shield-soc/analyze/logs \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{"logs": ["FAILED LOGIN user=admin ip=1.2.3.4", "SUCCESS LOGIN user=admin ip=1.2.3.4"], "source": "auth"}'
```

---

## Response threat levels

`safe` → `low` → `medium` → `high` → `critical`

---

## Tech stack

- **API**: FastAPI + Python 3.12
- **AI engine**: Claude claude-sonnet-4-20250514 (Anthropic)
- **Auth**: API key header (`X-API-Key`)
- **Docs**: Auto-generated at `/docs`

---

## Project structure

```
sentinelmind/
├── api/
│   ├── main.py              # App entry point
│   ├── core/
│   │   ├── config.py        # Settings
│   │   └── auth.py          # API key auth
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── shield_id.py
│   │   ├── shield_phish.py
│   │   ├── shield_dev.py
│   │   └── shield_soc.py
│   └── services/
│       ├── shield_id_service.py
│       ├── shield_phish_service.py
│       ├── shield_dev_service.py
│       └── shield_soc_service.py
├── tests/
│   └── test_api.py
├── .env.example
├── requirements.txt
└── run.bat
```

---

Built by SentinelMind · v0.1.0
