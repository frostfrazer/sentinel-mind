from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from api.auth.database import get_db
from api.auth.dependencies import get_current_user
from api.auth.models import User, PlanTier
from api.auth.schemas import PlanInfo, CheckoutResponse
from api.auth.billing import (
    create_paystack_customer, initialize_transaction,
    verify_transaction, cancel_subscription,
    verify_webhook_signature, PLAN_DISPLAY
)
from api.auth.service import PLAN_LIMITS

router = APIRouter()


class CheckoutRequest(BaseModel):
    plan: PlanTier
    callback_url: str   # where Paystack redirects after payment


class VerifyRequest(BaseModel):
    reference: str


# ── Plans ──────────────────────────────────────────────────────────────────
@router.get("/plans")
async def list_plans():
    """All available plans with pricing in USD and KES."""
    return {
        tier.value: {
            **PLAN_DISPLAY[tier],
            "limits": PLAN_LIMITS[tier],
        }
        for tier in PlanTier
    }


# ── Current billing status ─────────────────────────────────────────────────
@router.get("/billing", response_model=PlanInfo)
async def get_billing(current_user: User = Depends(get_current_user)):
    return PlanInfo(
        plan=current_user.plan,
        daily_limit=PLAN_LIMITS[current_user.plan]["daily"],
        monthly_limit=PLAN_LIMITS[current_user.plan]["monthly"],
        stripe_customer_id=current_user.stripe_customer_id,       # reused for paystack_customer_code
        stripe_subscription_id=current_user.stripe_subscription_id,  # reused for paystack_subscription_code
    )


# ── Initialize payment ─────────────────────────────────────────────────────
@router.post("/billing/checkout", response_model=CheckoutResponse)
async def start_checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.plan == PlanTier.FREE:
        raise HTTPException(status_code=400, detail="Cannot checkout to free plan")

    # Create Paystack customer if first time
    if not current_user.stripe_customer_id:
        code = await create_paystack_customer(
            current_user.email,
            current_user.full_name or ""
        )
        if code:
            current_user.stripe_customer_id = code
            await db.commit()

    txn = await initialize_transaction(
        email=current_user.email,
        plan=body.plan,
        callback_url=body.callback_url,
        metadata={"user_id": current_user.id, "plan": body.plan.value},
    )
    return CheckoutResponse(checkout_url=txn["authorization_url"])


# ── Verify payment after redirect ─────────────────────────────────────────
@router.post("/billing/verify")
async def verify_payment(
    body: VerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Call this after Paystack redirects back to your callback_url.
    Paystack appends ?reference=... to the callback URL — pass it here.
    """
    try:
        txn = await verify_transaction(body.reference)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if txn.get("status") != "success":
        raise HTTPException(status_code=402, detail="Payment not successful")

    plan_value = txn.get("metadata", {}).get("plan")
    subscription_code = txn.get("subscription", {}).get("subscription_code", "")

    if plan_value:
        current_user.plan = PlanTier(plan_value)
    if subscription_code:
        current_user.stripe_subscription_id = subscription_code
    await db.commit()

    return {
        "message": f"Plan upgraded to {current_user.plan.value}",
        "plan": current_user.plan.value,
        "reference": body.reference,
    }


# ── Cancel subscription ────────────────────────────────────────────────────
@router.post("/billing/cancel")
async def cancel_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription found")

    # Paystack cancel requires subscription_code + email_token
    # Token is sent to user's email by Paystack — they paste it here
    raise HTTPException(
        status_code=400,
        detail="To cancel, use /billing/cancel/confirm with the token sent to your email"
    )


class CancelConfirmRequest(BaseModel):
    token: str  # emailed by Paystack to customer


@router.post("/billing/cancel/confirm")
async def cancel_confirm(
    body: CancelConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    success = await cancel_subscription(current_user.stripe_subscription_id, body.token)
    if not success:
        raise HTTPException(status_code=400, detail="Cancellation failed — check your token")

    current_user.plan = PlanTier.FREE
    current_user.stripe_subscription_id = None
    await db.commit()
    return {"message": "Subscription cancelled. Plan downgraded to Free."}


# ── Paystack webhook ───────────────────────────────────────────────────────
@router.post("/billing/webhook", include_in_schema=False)
async def paystack_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    if not verify_webhook_signature(payload, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event = await request.json()
    event_type = event.get("event")
    data = event.get("data", {})

    # Subscription created / charged successfully
    if event_type in ("charge.success", "subscription.create"):
        customer_email = data.get("customer", {}).get("email")
        plan_code = data.get("plan", {}).get("plan_code", "")
        sub_code = data.get("subscription_code", "")

        # Match plan_code back to our PlanTier
        from api.auth.billing import PAYSTACK_PLAN_CODES
        plan_tier = None
        for tier, code in PAYSTACK_PLAN_CODES.items():
            if code == plan_code:
                plan_tier = tier
                break

        if customer_email and plan_tier:
            result = await db.execute(select(User).where(User.email == customer_email))
            user = result.scalar_one_or_none()
            if user:
                user.plan = plan_tier
                if sub_code:
                    user.stripe_subscription_id = sub_code
                await db.commit()

    # Subscription disabled / cancelled
    elif event_type == "subscription.disable":
        customer_email = data.get("customer", {}).get("email")
        if customer_email:
            result = await db.execute(select(User).where(User.email == customer_email))
            user = result.scalar_one_or_none()
            if user:
                user.plan = PlanTier.FREE
                user.stripe_subscription_id = None
                await db.commit()

    return {"received": True}
