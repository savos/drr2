"""Authentication schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    firstname: str = Field(..., min_length=1, max_length=64)
    lastname: str = Field(..., min_length=1, max_length=64)
    email: EmailStr = Field(..., max_length=64)
    password: str = Field(..., min_length=8)
    company_name: str = Field(..., min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format: string@string.string"""
        email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()  # Store emails in lowercase

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least 1 uppercase letter")

        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least 1 lowercase letter")

        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least 1 number")

        special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_characters for c in v):
            raise ValueError("Password must contain at least 1 special character")

        return v


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        """Convert email to lowercase for case-insensitive comparison."""
        return v.lower()


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class PasswordStrengthRequest(BaseModel):
    """Schema for password strength validation request."""
    password: str


class PasswordStrengthResponse(BaseModel):
    """Schema for password strength validation response."""
    is_valid: bool
    message: str
    strength: str  # weak, medium, strong
