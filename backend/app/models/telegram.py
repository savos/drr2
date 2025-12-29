"""Telegram integration model for storing user chat configurations (DMs and groups)."""
import enum
from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, CHAR, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.config.database import Base


class TelegramStatus(str, enum.Enum):
    """Enum for Telegram integration status."""
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    ACTIVE = "ACTIVE"


class TelegramChatType(str, enum.Enum):
    """Enum for Telegram chat types."""
    PRIVATE = "private"      # DM with user
    GROUP = "group"          # Regular group
    SUPERGROUP = "supergroup"  # Supergroup
    CHANNEL = "channel"      # Channel


class Telegram(Base):
    """Telegram integration model for user chats (DMs and groups)."""
    __tablename__ = "telegram"
    __table_args__ = {"extend_existing": True}

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    telegram_user_id = Column(BigInteger, nullable=True, comment="Telegram user ID who connected this chat")
    channel_id = Column(BigInteger, nullable=False, comment="Chat ID: user's chat_id for DMs, group chat_id for groups")
    chat_type = Column(String(20), nullable=False, default="private", comment="Type of chat: private, group, supergroup, or channel")
    chat_title = Column(String(255), nullable=True, comment="Chat title for groups/channels, NULL for DMs")
    username = Column(String(255), nullable=True, comment="User's Telegram username")
    first_name = Column(String(255), nullable=True, comment="User's first name")
    last_name = Column(String(255), nullable=True, comment="User's last name")
    language_code = Column(String(16), nullable=True, comment="User's language code")
    status = Column(
        SQLAlchemyEnum(TelegramStatus, native_enum=False, length=16),
        nullable=False,
        default=TelegramStatus.DISABLED,
        comment="Status of Telegram integration: Disabled, Enabled, or Active"
    )
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, comment="Soft delete timestamp")

    # Relationship to user
    user = relationship("User", back_populates="telegram_connections")


# Alias for backward compatibility
TelegramDMConnection = Telegram
