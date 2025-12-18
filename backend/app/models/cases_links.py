"""Cases Links model for storing URLs related to case studies."""
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class CaseLink(Base):
    """CaseLink model for storing links related to cases."""
    __tablename__ = "cases_links"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    link = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationship to case
    case = relationship("Case", back_populates="links")
