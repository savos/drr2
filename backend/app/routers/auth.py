"""Authentication router for user registration and login."""
import os
import uuid
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.models.company import Company
from app.models.users import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    PasswordStrengthRequest,
    PasswordStrengthResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
    VerificationResponse,
    SetPasswordRequest,
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    validate_password_strength,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    generate_reset_token,
    verify_reset_token,
    get_reset_token_expiry,
    is_reset_token_expired,
)
from app.services.email import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with company.

    Security features:
    - Email validation and normalization
    - Strong password requirements
    - Bcrypt password hashing
    - Automatic company creation
    - JWT token generation
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == request.email.lower())
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength (additional server-side validation)
    is_valid, message = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    try:
        # Create company first
        company = Company(
            id=str(uuid.uuid4()),
            name=request.company_name,
        )
        db.add(company)
        await db.flush()  # Flush to get company ID

        # Hash password with bcrypt
        hashed_password = hash_password(request.password)

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            company_id=company.id,
            firstname=request.firstname,
            lastname=request.lastname,
            email=request.email.lower(),
            hashed_password=hashed_password,
            verified=0,  # Not verified by default
            is_superuser=1,  # Users created via signup are superusers
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        await db.refresh(company)

        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "company_id": user.company_id,
                "company_name": company.name,
                "verified": user.verified,  # 0=unverified, 1=pending, 2=verified
                "is_superuser": bool(user.is_superuser),
            }
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


# Dummy hash for timing attack prevention (pre-computed bcrypt hash)
# This ensures we always do a bcrypt comparison even when user doesn't exist
_DUMMY_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.nFdDJlzQpOq6lqu"


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user with email and password.

    Security features:
    - Case-insensitive email comparison
    - Bcrypt password verification
    - JWT token generation
    - Secure error messages (no user enumeration)
    - Timing attack prevention (always performs bcrypt comparison)
    """
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == request.email.lower())
    )
    user = result.scalar_one_or_none()

    # Always perform password verification to prevent timing attacks
    # Use dummy hash if user doesn't exist to ensure constant-time response
    hash_to_check = user.hashed_password if user else _DUMMY_HASH
    password_valid = verify_password(request.password, hash_to_check)

    if not user or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is soft-deleted
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated"
        )

    # Get company information
    result = await db.execute(
        select(Company).where(Company.id == user.company_id)
    )
    company = result.scalar_one_or_none()

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "company_id": user.company_id,
            "company_name": company.name if company else None,
            "verified": user.verified,  # 0=unverified, 1=pending, 2=verified
            "is_superuser": bool(user.is_superuser),
        }
    )


@router.post("/validate-password", response_model=PasswordStrengthResponse)
async def validate_password(request: PasswordStrengthRequest):
    """
    Validate password strength.

    Returns password strength indicator and validation message.
    """
    is_valid, message = validate_password_strength(request.password)

    # Calculate strength level
    strength = "weak"
    if len(request.password) >= 8:
        checks = 0
        if any(c.isupper() for c in request.password):
            checks += 1
        if any(c.islower() for c in request.password):
            checks += 1
        if any(c.isdigit() for c in request.password):
            checks += 1
        special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_characters for c in request.password):
            checks += 1

        if checks >= 4:
            strength = "strong"
        elif checks >= 2:
            strength = "medium"

    return PasswordStrengthResponse(
        is_valid=is_valid,
        message=message,
        strength=strength
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    This is a debug endpoint to test authentication.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "firstname": current_user.firstname,
        "lastname": current_user.lastname,
        "verified": current_user.verified,  # 0=unverified, 1=pending, 2=verified
        "is_superuser": bool(current_user.is_superuser),
    }


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset email.

    Security features:
    - Always returns success message (prevents email enumeration)
    - Rate limiting should be implemented at reverse proxy level
    - Token is hashed before storage
    - Token expires after 1 hour
    """
    # Always respond with success to prevent email enumeration
    success_message = "If an account exists with this email, you will receive a password reset link shortly."

    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            # Return success even if user doesn't exist (prevents enumeration)
            logger.info(f"Password reset requested for non-existent email: {request.email}")
            return MessageResponse(message=success_message)

        # Check if user is deactivated
        if user.deleted_at is not None:
            logger.info(f"Password reset requested for deactivated user: {request.email}")
            return MessageResponse(message=success_message)

        # Generate reset token
        plain_token, hashed_token = generate_reset_token()

        # Store hashed token and expiry
        user.reset_token = hashed_token
        user.reset_token_expires = get_reset_token_expiry()

        await db.commit()

        # Build reset URL
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        reset_url = f"{frontend_url}/reset-password?token={plain_token}"

        # Send email
        email_sent = email_service.send_password_reset_email(
            to_email=user.email,
            reset_url=reset_url,
            user_name=user.firstname
        )

        if email_sent:
            logger.info(f"Password reset email sent to: {user.email}")
        else:
            logger.error(f"Failed to send password reset email to: {user.email}")

        return MessageResponse(message=success_message)

    except Exception as e:
        logger.error(f"Error in forgot_password: {e}")
        # Still return success to prevent information leakage
        return MessageResponse(message=success_message)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using token from email.

    Security features:
    - Token verification using constant-time comparison
    - Token expiration check
    - Token invalidation after use
    - Password strength validation
    """
    try:
        # Find user with matching reset token
        # We need to hash the incoming token and compare
        from app.utils.security import hash_reset_token

        incoming_token_hash = hash_reset_token(request.token)

        result = await db.execute(
            select(User).where(User.reset_token == incoming_token_hash)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("Password reset attempted with invalid token")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        # Check if token is expired
        if is_reset_token_expired(user.reset_token_expires):
            # Clear expired token
            user.reset_token = None
            user.reset_token_expires = None
            await db.commit()

            logger.warning(f"Password reset attempted with expired token for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        # Validate password strength
        is_valid, message = validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Update password
        user.hashed_password = hash_password(request.password)

        # Clear reset token (one-time use)
        user.reset_token = None
        user.reset_token_expires = None

        await db.commit()

        logger.info(f"Password successfully reset for user: {user.email}")

        return MessageResponse(
            message="Your password has been reset successfully. You can now log in with your new password."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in reset_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting your password"
        )


@router.get("/verify-reset-token")
async def verify_reset_token_endpoint(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify if a reset token is valid (for frontend validation).

    Returns success if token is valid and not expired.
    """
    try:
        from app.utils.security import hash_reset_token

        incoming_token_hash = hash_reset_token(token)

        result = await db.execute(
            select(User).where(User.reset_token == incoming_token_hash)
        )
        user = result.scalar_one_or_none()

        if not user or is_reset_token_expired(user.reset_token_expires):
            return {"valid": False, "message": "Invalid or expired reset token"}

        return {"valid": True, "message": "Token is valid"}

    except Exception as e:
        logger.error(f"Error verifying reset token: {e}")
        return {"valid": False, "message": "Invalid or expired reset token"}


@router.get("/verify-email", response_model=VerificationResponse, status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user's email address using token from email.

    Security features:
    - Token verification using constant-time comparison
    - Token expiration check
    - Token invalidation after use

    Returns whether user needs to set a password (for users added by superuser).
    """
    try:
        # Hash the incoming token and find user
        from app.utils.security import hash_reset_token

        incoming_token_hash = hash_reset_token(token)

        result = await db.execute(
            select(User).where(User.reset_token == incoming_token_hash)
        )
        user = result.scalar_one_or_none()

        if not user:
            # Token not found - check if user might already be verified
            # This happens when user refreshes page or clicks link twice
            logger.warning("Email verification attempted with invalid token")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token. If you already verified your email, please proceed to login or password creation."
            )

        # Check if token is expired
        if is_reset_token_expired(user.reset_token_expires):
            # Clear expired token
            user.reset_token = None
            user.reset_token_expires = None
            await db.commit()

            logger.warning(f"Email verification attempted with expired token for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )

        # Mark email as verified
        user.verified = 2  # 2 = verified

        # Check if user needs to set password (users added by superuser have no password)
        needs_password = user.hashed_password is None

        # Keep the token if user needs to set password, otherwise clear it
        verification_token = None
        if needs_password:
            # Generate new token for password setting (valid for 24 hours)
            from app.utils.security import generate_reset_token, get_verification_token_expiry
            plain_token, hashed_token = generate_reset_token()
            user.reset_token = hashed_token
            user.reset_token_expires = get_verification_token_expiry()
            verification_token = plain_token
        else:
            # Clear verification token (one-time use)
            user.reset_token = None
            user.reset_token_expires = None

        await db.commit()

        logger.info(f"Email successfully verified for user: {user.email}, needs_password: {needs_password}")

        return VerificationResponse(
            message="Your email has been verified successfully!",
            success=True,
            needs_password=needs_password,
            verification_token=verification_token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while verifying your email"
        )


@router.post("/set-password", response_model=TokenResponse)
async def set_password(
    request: SetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Set password for verified user who doesn't have one yet (users added by superuser).

    Security features:
    - Token verification
    - Email must be verified (verified=2)
    - User must not already have a password
    - Password strength validation
    - Auto-login after password is set
    """
    try:
        # Hash the incoming token and find user
        from app.utils.security import hash_reset_token

        incoming_token_hash = hash_reset_token(request.token)

        result = await db.execute(
            select(User).where(User.reset_token == incoming_token_hash)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("Set password attempted with invalid token")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )

        # Check if token is expired
        if is_reset_token_expired(user.reset_token_expires):
            user.reset_token = None
            user.reset_token_expires = None
            await db.commit()

            logger.warning(f"Set password attempted with expired token for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )

        # Check if user email is verified
        if user.verified != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email must be verified before setting password"
            )

        # Check if user already has a password
        if user.hashed_password is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a password"
            )

        # Validate password strength (already validated by Pydantic schema)
        # Hash and set password
        user.hashed_password = hash_password(request.password)

        # Clear token (one-time use)
        user.reset_token = None
        user.reset_token_expires = None

        await db.commit()
        await db.refresh(user)

        logger.info(f"Password successfully set for user: {user.email}")

        # Get company information
        result = await db.execute(
            select(Company).where(Company.id == user.company_id)
        )
        company = result.scalar_one_or_none()

        # Create access token for auto-login
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "company_id": user.company_id,
                "company_name": company.name if company else None,
                "verified": user.verified,
                "is_superuser": bool(user.is_superuser),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in set_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while setting your password"
        )
