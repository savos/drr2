"""Domain schemas for request/response validation."""
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict
from app.models.domain import DomainType


class DomainBase(BaseModel):
    """Base domain schema."""
    name: str = Field(..., max_length=256, description="Domain name or IP address")
    type: DomainType = Field(..., description="Type: DOMAIN or SSL")
    renew_date: date = Field(..., description="Date when service expires")
    not_before: datetime | None = Field(None, description="SSL certificate valid from date")
    issuer: str = Field(..., max_length=128, description="Who issued the service")
    issuer_link: str | None = Field(None, max_length=512, description="Website of issuer")


class DomainCreate(DomainBase):
    """Schema for creating a domain."""
    company_id: str = Field(..., max_length=36, description="Company ID")


class DomainUpdate(BaseModel):
    """Schema for updating a domain."""
    name: str | None = Field(None, max_length=256)
    type: DomainType | None = None
    renew_date: date | None = None
    not_before: datetime | None = None
    issuer: str | None = Field(None, max_length=128)
    issuer_link: str | None = Field(None, max_length=512)


class DomainResponse(DomainBase):
    """Schema for domain response."""
    id: int
    company_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )
