"""Pydantic schemas for Teams integrations."""
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TeamsStatus(str, Enum):
    """Enum for Teams connection status."""
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class TeamsBase(BaseModel):
    """Base schema for Teams DM connection."""
    tenant_id: str = Field(..., max_length=64)
    service_url: str = Field(..., max_length=512)
    conversation_id: str = Field(..., max_length=255)
    teams_user_id: str = Field(..., max_length=255)
    conversation_ref_json: Dict[str, Any]
    status: TeamsStatus = Field(default=TeamsStatus.DISABLED)


class TeamsCreate(TeamsBase):
    """Schema for creating a Teams DM connection."""
    user_id: str = Field(..., max_length=36)


class TeamsUpdate(BaseModel):
    """Schema for updating a Teams DM connection."""
    tenant_id: Optional[str] = Field(None, max_length=64)
    service_url: Optional[str] = Field(None, max_length=512)
    conversation_id: Optional[str] = Field(None, max_length=255)
    teams_user_id: Optional[str] = Field(None, max_length=255)
    conversation_ref_json: Optional[Dict[str, Any]] = None
    status: Optional[TeamsStatus] = None


class TeamsRead(TeamsBase):
    """Schema for reading a Teams DM connection."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
