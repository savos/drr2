"""Cases router for public case studies."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.models.cases import Case
from app.schemas.cases import CaseRead

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=List[CaseRead])
async def get_cases(db: AsyncSession = Depends(get_db)):
    """
    Get all case studies with their links.

    Public endpoint - no authentication required.
    Returns cases ordered by year descending.
    """
    result = await db.execute(
        select(Case)
        .options(selectinload(Case.links))
        .where(Case.deleted_at.is_(None))
        .order_by(Case.year.desc())
    )
    cases = result.scalars().all()
    return cases
