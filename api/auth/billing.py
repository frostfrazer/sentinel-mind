import httpx
import hashlib
import hmac
import json
from api.core.config import settings
from api.auth.models import PlanTier

PAYSTACK_BASE = "https://api.paystack.co"
HEADERS = {
    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}

# Paystack Plan Codes
PAYSTACK_PLAN_CODES = {
    PlanTier.STARTER:    "PLN_v3ytylhexxx8rw5",
    PlanTier.PRO:        "PLN_v96fptwrcxm62yj",
    PlanTier.ENTERPRISE: "PLN_4hdsij6ly5hsytm",
}

PLAN_DISPLAY = {
    PlanTier.FREE:       {"name": "Free",       "price": "$0/mo",    "price_kes": "KES 0/mo",    "scans": "50/day"},
    PlanTier.STARTER:    {"name": "Starter",    "price": "$49/mo",   "price_kes": "KES 6,500/mo","scans": "500/day"},
    PlanTier.PRO:        {"name": "Pro",        "price": "$199/mo",  "price_kes": "KES 26,000/mo","scans": "5,000/day"},
    PlanTier.ENTERPRISE: {"name": "Enterprise", "price": "Custom",   "price_kes": "Custom",       "scans": "Unlimited"},
}

PLAN_LIMITS = {
    PlanTier.FREE:       {"daily": 50,   "monthly": 500},
    PlanTier.STARTER:    {"daily": 500,  "monthly": 10_000},
    PlanTier.PRO:        {"daily": 5000, "monthly": 100_000},
    PlanTier.ENTERPRISE: {"daily": -1,   "monthly": -1},
}


async def create_paystack_customer(email: str, name: str) -> str:
    """Create a customer in Paystack and return their customer_code."""
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{PAYSTACK_BASE}/customer",
                headers=HEADERS,
                json={"email": email, "first_name": name.split()[0] if name else "", "last_name": " ".join(name.split()[1:]) if name else ""},
            )
            data = r.json()
            if data.get("status"):
                return data["data"]["customer_code"]
        except Exception:
            pass
    return ""


async def initialize_transaction(
    email: str,
    plan: PlanTier,
    callback_url: str,
    metadata: dict = {}
) -> dict:
    """
    Initialize a Paystack transaction/subscription.
    Returns {"authorization_url": ..., "access_code": ..., "reference": ...}
    """
    plan_code = PAYSTACK_PLAN_CODES.get(plan)
    if not plan_code:
        raise ValueError(f"No Paystack plan configured for: {plan}")

    # Amount in kobo/cents — Paystack uses smallest currency unit
    # For subscriptions, amount is 0 when plan_code is set
    payload = {
        "email": email,
        "amount": 0,          # Paystack uses plan amount when plan is set
        "plan": plan_code,
        "callback_url": callback_url,
        "metadata": {**metadata, "plan": plan.value},
        "channels": ["card", "mobile_money", "bank", "ussd"],
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{PAYSTACK_BASE}/transaction/initialize",
            headers=HEADERS,
            json=payload,
        )
        data = r.json()
        if not data.get("status"):
            raise ValueError(f"Paystack error: {data.get('message', 'Unknown error')}")
        return data["data"]


async def verify_transaction(reference: str) -> dict:
    """Verify a completed transaction by reference."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{PAYSTACK_BASE}/transaction/verify/{reference}",
            headers=HEADERS,
        )
        data = r.json()
        if not data.get("status"):
            raise ValueError(f"Verification failed: {data.get('message')}")
        return data["data"]


async def get_subscription(subscription_code: str) -> dict:
    """Fetch a subscription by its code."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{PAYSTACK_BASE}/subscription/{subscription_code}",
            headers=HEADERS,
        )
        return r.json().get("data", {})


async def cancel_subscription(subscription_code: str, token: str) -> bool:
    """Disable a subscription."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{PAYSTACK_BASE}/subscription/disable",
            headers=HEADERS,
            json={"code": subscription_code, "token": token},
        )
        return r.json().get("status", False)


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify that a webhook came from Paystack."""
    expected = hmac.new(
        settings.PAYSTACK_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
