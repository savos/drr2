"""Authentication router for user registration and login."""
import uuid
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
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    validate_password_strength,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

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
                "verified": bool(user.verified),
                "is_superuser": bool(user.is_superuser),
            }
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


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
    """
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == request.email.lower())
    )
    user = result.scalar_one_or_none()

    # Use constant-time comparison to prevent timing attacks
    if not user or not verify_password(request.password, user.hashed_password):
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
            "verified": bool(user.verified),
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
