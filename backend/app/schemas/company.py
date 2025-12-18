"""Company schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str = Field(..., max_length=255)
    payable: bool = False
    price_plan_id: str | None = None


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    name: str | None = Field(None, max_length=255)
    payable: bool | None = None
    price_plan_id: str | None = None


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True
