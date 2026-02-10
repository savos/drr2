"""Pricing model."""
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Pricing(Base):
    """Pricing/Price Plan model."""
    __tablename__ = "pricing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    plan_description = Column(Text, nullable=False)
    min_domains = Column(Integer, nullable=False, default=0)
    max_domains = Column(Integer, nullable=True)
    max_users = Column(Integer, nullable=False, default=1)
    monthly_price = Column(Float, nullable=False)
    yearly_price = Column(Float, nullable=False)
    per_domain_overage_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    companies = relationship("Company", back_populates="price_plan")
    subscriptions = relationship("Subscription", back_populates="plan")

    def calculate_monthly_price(self, actual_domains: int) -> float:
        """Calculate monthly price including per-domain overage for open-ended plans."""
        if self.per_domain_overage_price and actual_domains > self.min_domains:
            return self.monthly_price + (actual_domains - self.min_domains) * self.per_domain_overage_price
        return self.monthly_price

    def __repr__(self):
        return f"<Pricing(name={self.name}, max_domains={self.max_domains})>"
