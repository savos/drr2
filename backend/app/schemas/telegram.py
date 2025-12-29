"""Pydantic schemas for Telegram integrations (DMs and groups)."""
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TelegramStatus(str, Enum):
    """Enum for Telegram integration status."""
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    ACTIVE = "ACTIVE"


class TelegramChatType(str, Enum):
    """Enum for Telegram chat types."""
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class TelegramBase(BaseModel):
    """Base schema for Telegram integration."""
    telegram_user_id: Optional[int] = Field(None, description="Telegram user ID who connected this chat")
    channel_id: int = Field(..., description="Chat ID: user's chat_id for DMs, group chat_id for groups")
    chat_type: TelegramChatType = Field(default=TelegramChatType.PRIVATE, description="Type of chat")
    chat_title: Optional[str] = Field(None, max_length=255, description="Chat title for groups/channels, NULL for DMs")
    username: Optional[str] = Field(None, max_length=255, description="User's Telegram username")
    first_name: Optional[str] = Field(None, max_length=255, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=255, description="User's last name")
    language_code: Optional[str] = Field(None, max_length=16, description="User's language code")
    status: TelegramStatus = Field(default=TelegramStatus.DISABLED)


class TelegramCreate(TelegramBase):
    """Schema for creating a Telegram integration."""
    user_id: str = Field(..., max_length=36)


class TelegramUpdate(BaseModel):
    """Schema for updating a Telegram integration."""
    telegram_user_id: Optional[int] = None
    chat_type: Optional[TelegramChatType] = None
    chat_title: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    language_code: Optional[str] = Field(None, max_length=16)
    status: Optional[TelegramStatus] = None


class TelegramRead(TelegramBase):
    """Schema for reading a Telegram integration."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
