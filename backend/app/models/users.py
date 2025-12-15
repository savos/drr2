"""User model."""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from fastapi_users_db_sqlalchemy import GUID
from app.config.database import Base


class User(Base):
    """User model with authentication fields."""
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Optional profile fields
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(email={self.email})>"
