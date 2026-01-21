"""Users router for user management by superusers."""
import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.models.users import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.utils.security import (
    hash_password,
    validate_password_strength,
    get_current_superuser,
)

logger = logging.getLogger(__name__)

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
    - Password is optional (users added by superuser may not have password)
    - If password provided, strong password requirements apply
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

    # If password is provided, validate strength and hash it
    hashed_password = None
    if user_data.password:
        is_valid, message = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        hashed_password = hash_password(user_data.password)

    try:
        # Create user with specified is_superuser value
        # Password can be None for users added by superuser
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


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    List all users in the current user's company (superuser only).

    Returns users that are not soft-deleted.
    """
    try:
        result = await db.execute(
            select(User)
            .where(User.company_id == current_user.company_id)
            .where(User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
        )
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get a specific user by ID (superuser only).
    """
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .where(User.company_id == current_user.company_id)
        .where(User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Update a user (superuser only).

    Security features:
    - Only accessible by superusers
    - Can only update users in the same company
    - Email uniqueness check if email is being changed
    - Cannot demote the last superuser
    """
    # Get the user to update
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .where(User.company_id == current_user.company_id)
        .where(User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # If changing email, check uniqueness
    if user_data.email and user_data.email.lower() != user.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email.lower())
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # If demoting from superuser, check this isn't the last superuser
    if user_data.is_superuser is False and user.is_superuser:
        result = await db.execute(
            select(User)
            .where(User.company_id == current_user.company_id)
            .where(User.is_superuser == 1)
            .where(User.deleted_at.is_(None))
        )
        superusers = result.scalars().all()
        if len(superusers) <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove superuser status. At least one superuser must exist."
            )

    try:
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'email' and value:
                value = value.lower()
            if field == 'is_superuser':
                value = 1 if value else 0
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)

        logger.info(f"User {user_id} updated by superuser {current_user.id}")
        return user

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Soft delete a user (superuser only).

    Security features:
    - Only accessible by superusers
    - Can only delete users in the same company
    - Cannot delete yourself
    - Cannot delete the last superuser
    """
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account from here. Use account settings."
        )

    # Get the user to delete
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .where(User.company_id == current_user.company_id)
        .where(User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # If deleting a superuser, check this isn't the last one
    if user.is_superuser:
        result = await db.execute(
            select(User)
            .where(User.company_id == current_user.company_id)
            .where(User.is_superuser == 1)
            .where(User.deleted_at.is_(None))
        )
        superusers = result.scalars().all()
        if len(superusers) <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last superuser"
            )

    try:
        # Soft delete by setting deleted_at
        from datetime import datetime, timezone
        user.deleted_at = datetime.now(timezone.utc)

        await db.commit()

        logger.info(f"User {user_id} soft-deleted by superuser {current_user.id}")
        return {"message": "User deleted successfully", "success": True}

    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
