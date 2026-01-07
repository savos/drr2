"""Teams bot conversation references for proactive messaging."""
from sqlalchemy import Column, BigInteger, String, DateTime, func, ForeignKey, CHAR, UniqueConstraint, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.config.database import Base


class TeamsConversation(Base):
    __tablename__ = "teams_conversations"
    __table_args__ = (
        UniqueConstraint('conversation_id', name='uq_conversation_id'),
        {"extend_existing": True},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scope = Column(String(16), nullable=False, comment="Scope: personal or team")
    service_url = Column(Text, nullable=False, comment="Bot Framework serviceUrl")
    conversation_id = Column(String(255), nullable=False, comment="Conversation ID for proactive messages")
    team_id = Column(String(255), nullable=True, comment="Team ID if scope=team")
    channel_id = Column(String(255), nullable=True, comment="Channel ID if scope=team")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")

