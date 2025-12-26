"""Microsoft Teams integration model for storing user DM and team channel configurations."""
import enum
from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, CHAR, Enum as SQLAlchemyEnum, UniqueConstraint, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.config.database import Base


class TeamsStatus(str, enum.Enum):
    """Enum for Microsoft Teams integration status."""
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    ACTIVE = "ACTIVE"


class Teams(Base):
    """Microsoft Teams integration model for user DMs and team channels."""
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', 'channel_id', name='uq_user_team_channel'),
        {"extend_existing": True}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    teams_user_id = Column(String(255), nullable=False, comment="Microsoft Teams user ID")
    email = Column(String(255), nullable=True, comment="User's email address")
    username = Column(String(255), nullable=True, comment="User's display name")
    team_id = Column(String(255), nullable=True, comment="Teams team ID - NULL for DMs")
    team_name = Column(String(255), nullable=True, comment="Teams team name - NULL for DMs")
    channel_id = Column(String(255), nullable=True, comment="Teams channel ID - NULL for DMs")
    channel_name = Column(String(255), nullable=True, comment="Teams channel name - NULL for DMs")
    access_token = Column(Text, nullable=True, comment="Encrypted OAuth access token")
    refresh_token = Column(Text, nullable=True, comment="Encrypted OAuth refresh token")
    token_expires_at = Column(DateTime, nullable=True, comment="Access token expiration timestamp")
    status = Column(
        SQLAlchemyEnum(TeamsStatus, native_enum=False, length=16),
        nullable=False,
        default=TeamsStatus.DISABLED,
        comment="Status of Teams integration: DISABLED, ENABLED, or ACTIVE"
    )
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, comment="Soft delete timestamp")

    # Relationship to user
    user = relationship("User", back_populates="teams_connections")
