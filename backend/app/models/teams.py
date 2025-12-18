"""Teams DM connections model for storing user integrations."""
import enum
from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, CHAR, Enum as SQLAlchemyEnum, JSON
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.config.database import Base


class TeamsStatus(str, enum.Enum):
    """Enum for Teams connection status."""
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class TeamsDMConnection(Base):
    """Teams DM connection model for user integrations."""
    __tablename__ = "teams"
    __table_args__ = {"extend_existing": True}

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(64), nullable=False)
    service_url = Column(String(512), nullable=False)
    conversation_id = Column(String(255), nullable=False)
    teams_user_id = Column(String(255), nullable=False)
    conversation_ref_json = Column(JSON, nullable=False)
    status = Column(
        SQLAlchemyEnum(TeamsStatus, native_enum=False, length=16),
        nullable=False,
        default=TeamsStatus.DISABLED,
        comment="Status of Teams connection: Disabled, Enabled, Active, or Inactive"
    )
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationship to user
    user = relationship("User", back_populates="teams_connections")
