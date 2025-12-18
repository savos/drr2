"""Discord DM connections model for storing user integrations."""
import enum
from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, CHAR, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.config.database import Base


class DiscordStatus(str, enum.Enum):
    """Enum for Discord connection status."""
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Discord(Base):
    """Discord model for user integrations."""
    __tablename__ = "discord"
    __table_args__ = {"extend_existing": True}

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    discord_user_id = Column(String(32), nullable=False)
    guild_id = Column(String(32), nullable=True)
    channel_id = Column(String(32), nullable=True)
    username = Column(String(255), nullable=True)
    global_name = Column(String(255), nullable=True)
    status = Column(
        SQLAlchemyEnum(DiscordStatus, native_enum=False, length=16),
        nullable=False,
        default=DiscordStatus.DISABLED,
        comment="Status of Discord connection: Disabled, Enabled, Active, or Inactive"
    )
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationship to user
    user = relationship("User", back_populates="discord_connections")
