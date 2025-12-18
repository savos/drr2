"""Telegram DM connections model for storing user chat integrations."""
import enum
from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, CHAR, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.config.database import Base


class TelegramStatus(str, enum.Enum):
    """Enum for Telegram connection status."""
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class TelegramDMConnection(Base):
    """Telegram DM connection model for user integrations."""
    __tablename__ = "telegram"
    __table_args__ = {"extend_existing": True}

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    telegram_user_id = Column(BigInteger, nullable=True)
    channel_id = Column(BigInteger, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(16), nullable=True)
    status = Column(
        SQLAlchemyEnum(TelegramStatus, native_enum=False, length=16),
        nullable=False,
        default=TelegramStatus.DISABLED,
        comment="Status of Telegram connection: Disabled, Enabled, Active, or Inactive"
    )
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationship to user
    user = relationship("User", back_populates="telegram_connections")
