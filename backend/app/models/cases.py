"""Cases model for storing real-world certificate/domain expiration case studies."""
import enum
from sqlalchemy import Column, Integer, String, DateTime, func, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.config.database import Base


class ProblemType(str, enum.Enum):
    """Enum for problem types."""
    DOMAIN = "Domain"
    SSL = "SSL"
    DOMAIN_SSL = "Domain, SSL"


class Case(Base):
    """Case model for real-world examples."""
    __tablename__ = "cases"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String(32), nullable=False)
    problem = Column(
        SQLAlchemyEnum(ProblemType, native_enum=False, length=20),
        nullable=False,
        comment="Type of problem: Domain, SSL, or Domain, SSL"
    )
    year = Column(Integer, nullable=False, comment="Year the incident occurred")
    heading = Column(String(64), nullable=False)
    text = Column(String(256), nullable=False)
    loss = Column(String(128), nullable=True, comment="Financial or reputation loss amount")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationship to links
    links = relationship("CaseLink", back_populates="case", cascade="all, delete-orphan")
