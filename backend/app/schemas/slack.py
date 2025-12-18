"""Pydantic schemas for Slack integrations."""
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SlackStatus(str, Enum):
    """Enum for Slack integration status."""
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ACTIVE = "Active"


class SlackBase(BaseModel):
    """Base schema for Slack integration."""
    workspace_id: str = Field(..., max_length=36)
    workspace_name: Optional[str] = Field(None, max_length=128)
    bot_token: str
    bot_user_id: Optional[str] = Field(None, max_length=32)
    slack_user_id: Optional[str] = Field(None, max_length=32)
    channel_id: Optional[str] = Field(None, max_length=32)
    status: SlackStatus = Field(default=SlackStatus.DISABLED)


class SlackCreate(SlackBase):
    """Schema for creating a Slack integration."""
    user_id: str = Field(..., max_length=36)


class SlackUpdate(BaseModel):
    """Schema for updating a Slack integration."""
    workspace_id: Optional[str] = Field(None, max_length=36)
    workspace_name: Optional[str] = Field(None, max_length=128)
    bot_token: Optional[str] = None
    bot_user_id: Optional[str] = Field(None, max_length=32)
    slack_user_id: Optional[str] = Field(None, max_length=32)
    channel_id: Optional[str] = Field(None, max_length=32)
    status: Optional[SlackStatus] = None


class SlackRead(SlackBase):
    """Schema for reading a Slack integration."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
