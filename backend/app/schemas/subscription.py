"""Subscription schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""
    id: int
    company_id: str
    plan_id: int
    billing_cycle: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    actual_domain_count: int
    overage_amount: float
    stripe_subscription_id: str | None = None
    stripe_customer_id: str | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
