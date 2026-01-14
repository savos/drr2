"""Slack integration model for storing workspace and channel configurations."""
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, CHAR, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.config.database import Base


class SlackStatus(str, enum.Enum):
    """Enum for Slack integration status."""
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ACTIVE = "Active"


class Slack(Base):
    """Slack model for workspace integrations."""
    __tablename__ = "slack"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(CHAR(36), nullable=False)
    workspace_name = Column(String(128), nullable=True)
    bot_token = Column(Text, nullable=False)
    bot_user_id = Column(String(32), nullable=True)
    slack_user_id = Column(String(32), nullable=True)
    user_token = Column(Text, nullable=True, comment="Slack user access token for listing user-created channels")
    channel_id = Column(String(32), nullable=False, comment="DM channel ID (slack_user_id) or group channel ID")
    channel_name = Column(String(255), nullable=True, comment="Channel name for group channels, NULL for DMs")
    status = Column(
        SQLAlchemyEnum(SlackStatus, native_enum=False, length=20),
        nullable=False,
        default=SlackStatus.DISABLED,
        comment="Status of Slack integration: Disabled, Enabled, or Active"
    )
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationship to user
    user = relationship("User", back_populates="slack_integrations")
