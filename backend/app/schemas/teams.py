"""Pydantic schemas for Microsoft Teams integrations."""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class TeamsStatus(str, Enum):
    """Enum for Teams integration status."""
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    ACTIVE = "ACTIVE"


class TeamsBase(BaseModel):
    """Base schema for Teams integration."""
    teams_user_id: str = Field(..., max_length=255)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, max_length=255)
    team_id: Optional[str] = Field(None, max_length=255)
    team_name: Optional[str] = Field(None, max_length=255)
    channel_id: Optional[str] = Field(None, max_length=255)
    channel_name: Optional[str] = Field(None, max_length=255)
    status: TeamsStatus = Field(default=TeamsStatus.DISABLED)


class TeamsCreate(TeamsBase):
    """Schema for creating a Teams integration."""
    user_id: str = Field(..., max_length=36)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class TeamsUpdate(BaseModel):
    """Schema for updating a Teams integration."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, max_length=255)
    team_id: Optional[str] = Field(None, max_length=255)
    team_name: Optional[str] = Field(None, max_length=255)
    channel_id: Optional[str] = Field(None, max_length=255)
    channel_name: Optional[str] = Field(None, max_length=255)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    status: Optional[TeamsStatus] = None


class TeamsRead(BaseModel):
    """Schema for reading a Teams integration."""
    id: int
    user_id: str
    teams_user_id: str
    email: Optional[str] = None
    username: Optional[str] = None
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    status: TeamsStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChannelSelection(BaseModel):
    """Schema for channel selection from modal."""
    team_id: str
    team_name: str
    channel_id: str
    channel_name: str


class AddChannelsRequest(BaseModel):
    """Schema for adding multiple channels."""
    channels: List[ChannelSelection]
