"""User schemas for request/response validation."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field


# Type for notification channel status
NotificationStatus = Literal['disabled', 'enabled', 'verifying', 'verified']


class UserBase(BaseModel):
    """Base user schema."""
    firstname: str = Field(..., max_length=64)
    lastname: str = Field(..., max_length=64)
    position: str | None = Field(None, max_length=64)
    email: EmailStr = Field(..., max_length=64)


class UserCreate(UserBase):
    """Schema for creating a user."""
    company_id: str = Field(..., max_length=36)
    password: str | None = Field(None, min_length=8)  # Optional - users added by superuser may not have password
    is_superuser: bool = False

    # Optional notification preferences
    notifications: NotificationStatus = 'disabled'
    slack: NotificationStatus = 'disabled'
    teams: NotificationStatus = 'disabled'
    discord: NotificationStatus = 'disabled'
    telegram: NotificationStatus = 'disabled'


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    firstname: str | None = Field(None, max_length=64)
    lastname: str | None = Field(None, max_length=64)
    position: str | None = Field(None, max_length=64)
    email: EmailStr | None = Field(None, max_length=64)
    is_superuser: bool | None = None

    # Notification preferences
    notifications: NotificationStatus | None = None
    slack: NotificationStatus | None = None
    teams: NotificationStatus | None = None
    discord: NotificationStatus | None = None
    telegram: NotificationStatus | None = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    company_id: str
    verified: bool
    is_superuser: bool

    # Notification channel status
    notifications: str
    slack: str
    teams: str
    discord: str
    telegram: str

    # Timestamps
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True
