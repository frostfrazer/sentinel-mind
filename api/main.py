from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import shield_id, shield_phish, shield_dev, shield_soc
from api.routers import auth, users, billing
from api.auth.database import init_db
from api.core.config import settings

app = FastAPI(
    title="SentinelMind API",
    description="AI-native cybersecurity platform — identity, threats, code & human layer",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

# ── Auth & users ───────────────────────────────────────────────────────────
app.include_router(auth.router,    prefix="/v1/auth",    tags=["Auth"])
app.include_router(users.router,   prefix="/v1/users",   tags=["Users"])
app.include_router(billing.router, prefix="/v1/billing", tags=["Billing"])

# ── AI pillars ─────────────────────────────────────────────────────────────
app.include_router(shield_id.router,    prefix="/v1/shield-id",    tags=["Shield ID"])
app.include_router(shield_phish.router, prefix="/v1/shield-phish", tags=["Shield Phish"])
app.include_router(shield_dev.router,   prefix="/v1/shield-dev",   tags=["Shield Dev"])
app.include_router(shield_soc.router,   prefix="/v1/shield-soc",   tags=["Shield SOC"])

@app.get("/", tags=["Health"])
def root():
    return {"name": "SentinelMind", "version": "0.1.0", "status": "running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
