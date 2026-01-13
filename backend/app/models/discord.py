"""Discord integration model for storing user DM and server channel configurations."""
import enum
from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, CHAR, Enum as SQLAlchemyEnum, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.config.database import Base


class DiscordStatus(str, enum.Enum):
    """Enum for Discord integration status."""
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    ACTIVE = "ACTIVE"


class Discord(Base):
    """Discord integration model for user DMs and server channels."""
    __tablename__ = "discord"
    __table_args__ = (
        UniqueConstraint('user_id', 'guild_id', 'channel_id', name='uq_user_guild_channel'),
        {"extend_existing": True}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    discord_user_id = Column(String(32), nullable=False, comment="Discord user ID")
    guild_id = Column(String(32), nullable=True, comment="Discord server (guild) ID - NULL for DMs")
    guild_name = Column(String(255), nullable=True, comment="Discord server (guild) name - NULL for DMs")
    channel_id = Column(String(32), nullable=True, comment="Discord channel ID - NULL for DMs")
    channel_name = Column(String(255), nullable=True, comment="Discord channel name - NULL for DMs")
    username = Column(String(255), nullable=True, comment="Discord username")
    global_name = Column(String(255), nullable=True, comment="Discord display name")
    owned_guild_ids = Column(String(2000), nullable=True, comment="Comma-separated list of guild IDs user owns")
    status = Column(
        SQLAlchemyEnum(DiscordStatus, native_enum=False, length=16),
        nullable=False,
        default=DiscordStatus.DISABLED,
        comment="Status of Discord integration: DISABLED, ENABLED, or ACTIVE"
    )
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, comment="Soft delete timestamp")

    # Relationship to user
    user = relationship("User", back_populates="discord_connections")
