"""Pricing router - public endpoint for pricing plans."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.models.pricing import Pricing
from app.schemas.pricing import PricingResponse

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/", response_model=List[PricingResponse])
async def get_pricing_plans(db: AsyncSession = Depends(get_db)):
    """Return all active pricing plans ordered by monthly price."""
    result = await db.execute(
        select(Pricing)
        .where(Pricing.deleted_at == None)
        .order_by(Pricing.monthly_price)
    )
    return result.scalars().all()
