"""Pydantic schemas for Discord integrations."""
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DiscordStatus(str, Enum):
    """Enum for Discord connection status."""
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class DiscordBase(BaseModel):
    """Base schema for Discord connection."""
    discord_user_id: str = Field(..., max_length=32)
    guild_id: Optional[str] = Field(None, max_length=32)
    channel_id: Optional[str] = Field(None, max_length=32)
    username: Optional[str] = Field(None, max_length=255)
    global_name: Optional[str] = Field(None, max_length=255)
    status: DiscordStatus = Field(default=DiscordStatus.DISABLED)


class DiscordCreate(DiscordBase):
    """Schema for creating a Discord connection."""
    user_id: str = Field(..., max_length=36)


class DiscordUpdate(BaseModel):
    """Schema for updating a Discord connection."""
    discord_user_id: Optional[str] = Field(None, max_length=32)
    guild_id: Optional[str] = Field(None, max_length=32)
    channel_id: Optional[str] = Field(None, max_length=32)
    username: Optional[str] = Field(None, max_length=255)
    global_name: Optional[str] = Field(None, max_length=255)
    status: Optional[DiscordStatus] = None


class DiscordRead(DiscordBase):
    """Schema for reading a Discord connection."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
