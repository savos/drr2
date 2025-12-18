"""Pydantic schemas for cases and case links."""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class ProblemType(str, Enum):
    """Enum for problem types."""
    DOMAIN = "Domain"
    SSL = "SSL"
    DOMAIN_SSL = "Domain, SSL"


class CaseLinkBase(BaseModel):
    """Base schema for case link."""
    link: str = Field(..., max_length=512)


class CaseLinkCreate(CaseLinkBase):
    """Schema for creating a case link."""
    pass


class CaseLinkRead(CaseLinkBase):
    """Schema for reading a case link."""
    id: int
    case_id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseBase(BaseModel):
    """Base schema for case."""
    company: str = Field(..., max_length=32)
    problem: ProblemType
    year: int = Field(..., ge=1900, le=2100)
    heading: str = Field(..., max_length=64)
    text: str = Field(..., max_length=256)
    loss: Optional[str] = Field(None, max_length=128)


class CaseCreate(CaseBase):
    """Schema for creating a case."""
    links: Optional[List[CaseLinkCreate]] = None


class CaseUpdate(BaseModel):
    """Schema for updating a case."""
    company: Optional[str] = Field(None, max_length=32)
    problem: Optional[ProblemType] = None
    year: Optional[int] = Field(None, ge=1900, le=2100)
    heading: Optional[str] = Field(None, max_length=64)
    text: Optional[str] = Field(None, max_length=256)
    loss: Optional[str] = Field(None, max_length=128)


class CaseRead(CaseBase):
    """Schema for reading a case."""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    links: List[CaseLinkRead] = []

    class Config:
        from_attributes = True
