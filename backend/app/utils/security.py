"""Security utilities for password hashing and JWT token management."""
import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select

# Password hashing configuration with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
_jwt_secret = os.getenv("JWT_SECRET")
if not _jwt_secret:
    import warnings
    warnings.warn(
        "JWT_SECRET environment variable not set! Using auto-generated secret. "
        "This is insecure for production - set JWT_SECRET in your .env file.",
        RuntimeWarning
    )
    # Generate a random secret for this process (will change on restart)
    _jwt_secret = secrets.token_urlsafe(32)

SECRET_KEY = _jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing user data to encode in token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength according to security requirements.

    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least 1 uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least 1 lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least 1 number"

    special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_characters for c in password):
        return False, "Password must contain at least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"

    return True, "Password is strong"


# Password Reset Token Configuration
RESET_TOKEN_EXPIRE_HOURS = 1  # Password reset tokens expire after 1 hour
EMAIL_VERIFICATION_EXPIRE_HOURS = 24  # Email verification tokens expire after 24 hours


def generate_reset_token() -> Tuple[str, str]:
    """
    Generate a secure password reset token.

    Returns:
        Tuple of (plain_token, hashed_token)
        - plain_token: Send this to the user (in email link)
        - hashed_token: Store this in the database
    """
    # Generate a cryptographically secure random token
    plain_token = secrets.token_urlsafe(32)

    # Hash the token for storage (using SHA-256 for speed since tokens are already random)
    hashed_token = hashlib.sha256(plain_token.encode()).hexdigest()

    return plain_token, hashed_token


def hash_reset_token(token: str) -> str:
    """
    Hash a reset token for comparison.

    Args:
        token: Plain text reset token

    Returns:
        Hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_reset_token(plain_token: str, hashed_token: str) -> bool:
    """
    Verify a reset token against its hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        plain_token: Plain text token from user
        hashed_token: Hashed token from database

    Returns:
        True if tokens match
    """
    computed_hash = hash_reset_token(plain_token)
    return secrets.compare_digest(computed_hash, hashed_token)


def get_reset_token_expiry() -> datetime:
    """
    Get the expiration datetime for a new password reset token (1 hour).

    Returns:
        Datetime when the token will expire
    """
    return datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)


def get_verification_token_expiry() -> datetime:
    """
    Get the expiration datetime for a new email verification token (24 hours).

    Returns:
        Datetime when the token will expire
    """
    return datetime.now(timezone.utc) + timedelta(hours=EMAIL_VERIFICATION_EXPIRE_HOURS)


def is_reset_token_expired(expiry: Optional[datetime]) -> bool:
    """
    Check if a reset token has expired.

    Args:
        expiry: Token expiration datetime

    Returns:
        True if token is expired or expiry is None
    """
    if expiry is None:
        return True

    # Make expiry timezone-aware if it isn't
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc) > expiry


# HTTP Bearer token scheme
security = HTTPBearer()


from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current user from JWT token.

    Args:
        credentials: HTTP Authorization credentials with Bearer token
        db: Database session (injected by FastAPI)

    Returns:
        Current user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    from app.models.users import User
    import logging

    logger = logging.getLogger(__name__)

    token = credentials.credentials
    payload = decode_access_token(token)

    user_id: str = payload.get("user_id")
    logger.info(f"Decoded token, user_id: {user_id}")

    if user_id is None:
        logger.warning("No user_id in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # db is provided by FastAPI dependency injection

    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        logger.info(f"User query result: {user is not None}")

        if user is None:
            logger.warning(f"User not found for user_id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.deleted_at is not None:
            logger.warning(f"User {user_id} is deactivated")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated"
            )

        logger.info(f"Successfully authenticated user: {user.email}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_superuser(
    current_user = Depends(get_current_user)
):
    """
    Get the current user and verify they are a superuser.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current user object (verified as superuser)

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can perform this action"
        )
    return current_user
