"""Service for Teams conversation storage and retrieval."""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.teams_conversation import TeamsConversation

logger = logging.getLogger(__name__)


class TeamsConversationService:
    @staticmethod
    async def upsert_personal(
        db: AsyncSession,
        user_id: str,
        service_url: str,
        conversation_id: str,
    ) -> Optional[TeamsConversation]:
        try:
            result = await db.execute(
                select(TeamsConversation).where(
                    TeamsConversation.conversation_id == conversation_id
                )
            )
            row = result.scalar_one_or_none()
            if row:
                row.service_url = service_url
            else:
                row = TeamsConversation(
                    user_id=user_id,
                    scope="personal",
                    service_url=service_url,
                    conversation_id=conversation_id,
                )
                db.add(row)
            await db.commit()
            await db.refresh(row)
            return row
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"DB error upserting TeamsConversation: {e}")
            return None

    @staticmethod
    async def get_personal_by_user(
        db: AsyncSession,
        user_id: str,
    ) -> Optional[TeamsConversation]:
        try:
            result = await db.execute(
                select(TeamsConversation).where(
                    TeamsConversation.user_id == user_id,
                    TeamsConversation.scope == "personal",
                ).order_by(TeamsConversation.created_at.desc())
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"DB error getting TeamsConversation: {e}")
            return None

    @staticmethod
    async def upsert_team(
        db: AsyncSession,
        user_id: str,
        service_url: str,
        conversation_id: str,
        team_id: str,
        channel_id: str,
    ) -> Optional[TeamsConversation]:
        try:
            result = await db.execute(
                select(TeamsConversation).where(
                    TeamsConversation.conversation_id == conversation_id
                )
            )
            row = result.scalar_one_or_none()
            if row:
                row.service_url = service_url
                row.team_id = team_id
                row.channel_id = channel_id
                row.scope = "team"
            else:
                row = TeamsConversation(
                    user_id=user_id,
                    scope="team",
                    service_url=service_url,
                    conversation_id=conversation_id,
                    team_id=team_id,
                    channel_id=channel_id,
                )
                db.add(row)
            await db.commit()
            await db.refresh(row)
            return row
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"DB error upserting TeamsConversation team: {e}")
            return None
