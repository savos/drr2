"""Pydantic schemas for Telegram DM connections."""
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TelegramStatus(str, Enum):
    """Enum for Telegram connection status."""
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class TelegramBase(BaseModel):
    """Base schema for Telegram DM connection."""
    telegram_user_id: Optional[int] = None
    channel_id: int
    username: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    language_code: Optional[str] = Field(None, max_length=16)
    status: TelegramStatus = Field(default=TelegramStatus.DISABLED)


class TelegramCreate(TelegramBase):
    """Schema for creating a Telegram DM connection."""
    user_id: str = Field(..., max_length=36)


class TelegramUpdate(BaseModel):
    """Schema for updating a Telegram DM connection."""
    telegram_user_id: Optional[int] = None
    channel_id: Optional[int] = None
    username: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    language_code: Optional[str] = Field(None, max_length=16)
    status: Optional[TelegramStatus] = None


class TelegramRead(TelegramBase):
    """Schema for reading a Telegram DM connection."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
