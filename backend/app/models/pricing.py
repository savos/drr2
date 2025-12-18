"""Pricing model."""
import uuid
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Pricing(Base):
    """Pricing/Price Plan model."""
    __tablename__ = "pricing"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    plan_description = Column(Text, nullable=False)
    max_domains = Column(Integer, nullable=False)
    monthly_price = Column(Float, nullable=False)
    yearly_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    companies = relationship("Company", back_populates="price_plan")

    def __repr__(self):
        return f"<Pricing(name={self.name}, max_domains={self.max_domains})>"
