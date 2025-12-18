"""Users router for user management by superusers."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.models.users import User
from app.schemas.user import UserCreate, UserResponse
from app.utils.security import (
    hash_password,
    validate_password_strength,
    get_current_superuser,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Create a new user (superuser only).

    Security features:
    - Only accessible by superusers
    - Email validation and normalization
    - Strong password requirements
    - Bcrypt password hashing
    - Created user's is_superuser status is determined by the request
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email.lower())
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength
    is_valid, message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    try:
        # Hash password with bcrypt
        hashed_password = hash_password(user_data.password)

        # Create user with specified is_superuser value
        user = User(
            id=str(uuid.uuid4()),
            company_id=user_data.company_id,
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            position=user_data.position,
            email=user_data.email.lower(),
            hashed_password=hashed_password,
            verified=0,  # Not verified by default
            is_superuser=1 if user_data.is_superuser else 0,
            notifications=user_data.notifications,
            slack=user_data.slack,
            teams=user_data.teams,
            discord=user_data.discord,
            telegram=user_data.telegram,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User creation failed: {str(e)}"
        )
