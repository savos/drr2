"""Subscription model."""
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Subscription(Base):
    """Company subscription model tracking billing period, plan, and Stripe references."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("pricing.id"), nullable=False)
    billing_cycle = Column(Enum("monthly", "yearly"), nullable=False, default="monthly")
    status = Column(Enum("active", "trialing", "past_due", "cancelled"), nullable=False, default="active")
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    actual_domain_count = Column(Integer, nullable=False, default=0)
    overage_amount = Column(Float, nullable=False, default=0.0)
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    company = relationship("Company", back_populates="subscription")
    plan = relationship("Pricing", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(company_id={self.company_id}, plan_id={self.plan_id}, status={self.status})>"
