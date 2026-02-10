"""Pricing schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field


class PricingBase(BaseModel):
    """Base pricing schema."""
    name: str = Field(..., max_length=255)
    plan_description: str
    min_domains: int = Field(..., ge=0)
    max_domains: int | None = Field(None, ge=0)
    max_users: int = Field(..., ge=0)
    monthly_price: float = Field(..., ge=0)
    yearly_price: float = Field(..., ge=0)
    per_domain_overage_price: float | None = None


class PricingCreate(PricingBase):
    """Schema for creating a pricing plan."""
    pass


class PricingUpdate(BaseModel):
    """Schema for updating a pricing plan."""
    name: str | None = Field(None, max_length=255)
    plan_description: str | None = None
    min_domains: int | None = Field(None, ge=0)
    max_domains: int | None = Field(None, ge=0)
    max_users: int | None = Field(None, ge=0)
    monthly_price: float | None = Field(None, ge=0)
    yearly_price: float | None = Field(None, ge=0)
    per_domain_overage_price: float | None = Field(None, ge=0)


class PricingResponse(PricingBase):
    """Schema for pricing response."""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True
