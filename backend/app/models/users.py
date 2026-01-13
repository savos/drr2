"""User model."""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.config.database import Base


class User(Base):
    """User model with company association and notification preferences."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    firstname = Column(String(64), nullable=False)
    lastname = Column(String(64), nullable=False)
    position = Column(String(64), nullable=True, default=None)
    email = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)

    # Status fields
    verified = Column(Integer, default=0, nullable=False)  # tinyint(1): 0=False, 1=True
    is_superuser = Column(Integer, default=0, nullable=False)  # tinyint(1): 0=False, 1=True

    # Password reset fields
    reset_token = Column(String(256), nullable=True, default=None)  # Hashed reset token
    reset_token_expires = Column(DateTime, nullable=True, default=None)  # Token expiration

    # Notification channel status
    # Values: 'disabled', 'enabled', 'verifying', 'verified'
    notifications = Column(String(20), default='disabled', nullable=False)
    slack = Column(String(20), default='disabled', nullable=False)
    teams = Column(String(20), default='disabled', nullable=False)
    discord = Column(String(20), default='disabled', nullable=False)
    telegram = Column(String(20), default='disabled', nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    company = relationship("Company", back_populates="users")
    slack_integrations = relationship("Slack", back_populates="user", cascade="all, delete-orphan")
    telegram_connections = relationship("Telegram", back_populates="user", cascade="all, delete-orphan")
    discord_connections = relationship("Discord", back_populates="user", cascade="all, delete-orphan")
    teams_connections = relationship("Teams", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email={self.email}, name={self.firstname} {self.lastname})>"
