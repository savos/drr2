"""Company model."""
import uuid
from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class Company(Base):
    """Company model."""
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    payable = Column(Integer, default=0, nullable=False)  # tinyint(1): 0=False, 1=True
    price_plan_id = Column(Integer, ForeignKey("pricing.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    users = relationship("User", back_populates="company")
    price_plan = relationship("Pricing", back_populates="companies")
    domains = relationship("Domain", back_populates="company", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="company", uselist=False)

    def __repr__(self):
        return f"<Company(name={self.name})>"
