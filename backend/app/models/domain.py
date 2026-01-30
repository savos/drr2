from sqlalchemy import Column, Integer, String, Date, DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
import enum


class DomainType(enum.Enum):
    """Enum for domain/SSL type."""
    DOMAIN = "DOMAIN"
    SSL = "SSL"


class Domain(Base):
    __tablename__ = "domains"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, comment="Foreign key to companies table")
    name = Column(String(256), nullable=False, comment="Domain name or IP address")
    type = Column(Enum(DomainType), nullable=False, comment="Type: DOMAIN or SSL")
    renew_date = Column(Date, nullable=False, comment="Date when service expires")
    not_before = Column(DateTime, nullable=True, comment="SSL certificate valid from date")
    issuer = Column(String(128), nullable=False, comment="Who issued the service (registrar/CA)")
    issuer_link = Column(String(512), nullable=True, comment="Website of issuer")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="When record was created")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="When domain/SSL was last checked")
    deleted_at = Column(DateTime, nullable=True, comment="Soft delete timestamp")

    # Relationships
    company = relationship("Company", back_populates="domains")

    def __repr__(self):
        return f"<Domain(name={self.name}, type={self.type.value}, renew_date={self.renew_date})>"

