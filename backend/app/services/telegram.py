"""Telegram service for database operations."""
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.models.telegram import Telegram, TelegramStatus, TelegramChatType

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for Telegram database operations."""

    @staticmethod
    async def create_telegram_integration(
        db: AsyncSession,
        user_id: str,
        telegram_user_id: Optional[int],
        channel_id: int,
        chat_type: TelegramChatType,
        chat_title: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None,
        status: TelegramStatus = TelegramStatus.ENABLED
    ) -> Telegram:
        """
        Create a new Telegram integration for a specific chat (DM or group).

        Args:
            db: Database session
            user_id: DRR user ID
            telegram_user_id: Telegram user ID
            channel_id: Chat ID (telegram_user_id for DMs, group chat_id for groups)
            chat_type: Type of chat (private, group, supergroup, channel)
            chat_title: Chat title (NULL for DMs)
            username: User's Telegram username
            first_name: User's first name
            last_name: User's last name
            language_code: User's language code
            status: Integration status

        Returns:
            Created Telegram integration

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Check if this specific chat integration already exists (including soft-deleted)
            existing = await TelegramService.get_by_user_and_chat(
                db, user_id, channel_id, include_deleted=True
            )

            if existing:
                # Update existing integration (reactivate if soft-deleted)
                existing.telegram_user_id = telegram_user_id
                existing.chat_type = chat_type
                existing.chat_title = chat_title
                existing.username = username
                existing.first_name = first_name
                existing.last_name = last_name
                existing.language_code = language_code
                existing.status = status
                existing.deleted_at = None  # Reactivate if it was soft-deleted

                await db.commit()
                await db.refresh(existing)
                logger.info(f"Updated/reactivated Telegram integration for user {user_id}, chat {channel_id}")
                return existing

            # Create new integration
            telegram_integration = Telegram(
                user_id=user_id,
                telegram_user_id=telegram_user_id,
                channel_id=channel_id,
                chat_type=chat_type,
                chat_title=chat_title,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                status=status
            )

            db.add(telegram_integration)
            await db.commit()
            await db.refresh(telegram_integration)

            logger.info(f"Created Telegram integration for user {user_id}, chat {channel_id}")
            return telegram_integration

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error creating Telegram integration: {e}")
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, integration_id: int) -> Optional[Telegram]:
        """
        Get Telegram integration by ID.

        Args:
            db: Database session
            integration_id: Integration ID

        Returns:
            Telegram integration or None
        """
        try:
            result = await db.execute(
                select(Telegram).where(
                    Telegram.id == integration_id,
                    Telegram.deleted_at.is_(None)
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Telegram integration by ID: {e}")
            return None

    @staticmethod
    async def get_by_user_and_chat(
        db: AsyncSession,
        user_id: str,
        channel_id: int,
        include_deleted: bool = False
    ) -> Optional[Telegram]:
        """
        Get Telegram integration by user ID and chat ID.

        Args:
            db: Database session
            user_id: DRR user ID
            channel_id: Chat ID
            include_deleted: If True, includes soft-deleted integrations

        Returns:
            Telegram integration or None
        """
        try:
            query = select(Telegram).where(
                Telegram.user_id == user_id,
                Telegram.channel_id == channel_id
            )

            if not include_deleted:
                query = query.where(Telegram.deleted_at.is_(None))

            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Telegram integration: {e}")
            return None

    @staticmethod
    async def get_user_id_by_telegram_user(
        db: AsyncSession,
        telegram_user_id: int
    ) -> Optional[str]:
        """
        Resolve DRR user_id by Telegram user id from an existing DM integration.
        """
        try:
            result = await db.execute(
                select(Telegram).where(
                    Telegram.telegram_user_id == telegram_user_id,
                    Telegram.chat_type == TelegramChatType.PRIVATE,
                    Telegram.deleted_at.is_(None)
                ).order_by(Telegram.created_at.desc())
            )
            integ = result.scalar_one_or_none()
            return integ.user_id if integ else None
        except SQLAlchemyError as e:
            logger.error(f"Database error resolving user by telegram_user_id: {e}")
            return None

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> List[Telegram]:
        """
        Get all Telegram integrations for a user.

        Args:
            db: Database session
            user_id: DRR user ID

        Returns:
            List of Telegram integrations
        """
        try:
            result = await db.execute(
                select(Telegram).where(
                    Telegram.user_id == user_id,
                    Telegram.deleted_at.is_(None)
                ).order_by(Telegram.created_at.desc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user Telegram integrations: {e}")
            return []

    @staticmethod
    async def update_status(
        db: AsyncSession,
        integration_id: int,
        status: TelegramStatus
    ) -> Optional[Telegram]:
        """
        Update Telegram integration status.

        Args:
            db: Database session
            integration_id: Integration ID
            status: New status

        Returns:
            Updated Telegram integration or None
        """
        try:
            # Load ORM entity, update, commit, and return
            result = await db.execute(
                select(Telegram).where(Telegram.id == integration_id, Telegram.deleted_at.is_(None))
            )
            entity = result.scalar_one_or_none()
            if not entity:
                return None
            entity.status = status
            await db.commit()
            await db.refresh(entity)
            logger.info(f"Updated Telegram integration {integration_id} status to {status}")
            return entity

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating Telegram status: {e}")
            return None

    @staticmethod
    async def delete(db: AsyncSession, integration_id: int) -> bool:
        """
        Soft delete a Telegram integration.

        Args:
            db: Database session
            integration_id: Integration ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            from datetime import datetime

            result = await db.execute(
                select(Telegram).where(Telegram.id == integration_id, Telegram.deleted_at.is_(None))
            )
            entity = result.scalar_one_or_none()
            if not entity:
                return False
            entity.deleted_at = datetime.utcnow()
            entity.status = TelegramStatus.DISABLED
            await db.commit()
            logger.info(f"Deleted Telegram integration {integration_id}")
            return True

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting Telegram integration: {e}")
            return False

    @staticmethod
    async def get_active_integrations_by_user(
        db: AsyncSession,
        user_id: str
    ) -> List[Telegram]:
        """
        Get all active Telegram integrations for a user.

        Args:
            db: Database session
            user_id: DRR user ID

        Returns:
            List of active Telegram integrations
        """
        try:
            result = await db.execute(
                select(Telegram).where(
                    Telegram.user_id == user_id,
                    Telegram.status == TelegramStatus.ACTIVE,
                    Telegram.deleted_at.is_(None)
                ).order_by(Telegram.created_at.desc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error getting active Telegram integrations: {e}")
            return []


# Global instance
telegram_service = TelegramService()
