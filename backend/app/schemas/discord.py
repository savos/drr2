"""Pydantic schemas for Discord integrations (DMs and server channels)."""
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DiscordStatus(str, Enum):
    """Enum for Discord integration status."""
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    ACTIVE = "ACTIVE"


class DiscordBase(BaseModel):
    """Base schema for Discord integration."""
    discord_user_id: str = Field(..., max_length=32, description="Discord user ID")
    guild_id: Optional[str] = Field(None, max_length=32, description="Discord server (guild) ID - NULL for DMs")
    guild_name: Optional[str] = Field(None, max_length=255, description="Discord server (guild) name - NULL for DMs")
    channel_id: Optional[str] = Field(None, max_length=32, description="Discord channel ID - NULL for DMs")
    channel_name: Optional[str] = Field(None, max_length=255, description="Discord channel name - NULL for DMs")
    username: Optional[str] = Field(None, max_length=255, description="Discord username")
    global_name: Optional[str] = Field(None, max_length=255, description="Discord display name")
    status: DiscordStatus = Field(default=DiscordStatus.DISABLED)


class DiscordCreate(DiscordBase):
    """Schema for creating a Discord integration."""
    user_id: str = Field(..., max_length=36)


class DiscordUpdate(BaseModel):
    """Schema for updating a Discord integration."""
    guild_id: Optional[str] = Field(None, max_length=32)
    guild_name: Optional[str] = Field(None, max_length=255)
    channel_id: Optional[str] = Field(None, max_length=32)
    channel_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    global_name: Optional[str] = Field(None, max_length=255)
    status: Optional[DiscordStatus] = None


class DiscordRead(DiscordBase):
    """Schema for reading a Discord integration."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiscordOAuthResponse(BaseModel):
    """Schema for Discord OAuth callback response."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str


class DiscordUserResponse(BaseModel):
    """Schema for Discord user information."""
    id: str
    username: str
    global_name: Optional[str] = None
    discriminator: str
    avatar: Optional[str] = None


class TestConnectionResponse(BaseModel):
    """Response schema for test connection endpoint."""
    success: bool
    message: str
