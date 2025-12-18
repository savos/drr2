"""Slack service for database operations."""
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from app.models.slack import Slack, SlackStatus

logger = logging.getLogger(__name__)


class SlackService:
    """Service for Slack database operations."""

    @staticmethod
    async def create_slack_integration(
        db: AsyncSession,
        user_id: str,
        workspace_id: str,
        workspace_name: Optional[str],
        access_token: str,
        bot_user_id: Optional[str],
        slack_user_id: Optional[str],
        status: SlackStatus = SlackStatus.ENABLED
    ) -> Slack:
        """
        Create a new Slack integration.

        Args:
            db: Database session
            user_id: DRR user ID
            workspace_id: Slack workspace ID
            workspace_name: Slack workspace name
            access_token: Slack bot access token
            bot_user_id: Slack bot user ID
            slack_user_id: Slack user ID
            status: Integration status

        Returns:
            Created Slack integration

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Check if integration already exists
            existing = await SlackService.get_by_user_and_workspace(
                db, user_id, workspace_id
            )

            if existing:
                # Update existing integration
                existing.workspace_name = workspace_name
                existing.bot_token = access_token
                existing.bot_user_id = bot_user_id
                existing.slack_user_id = slack_user_id
                existing.status = status
                existing.deleted_at = None  # Reactivate if it was soft-deleted

                await db.commit()
                await db.refresh(existing)
                logger.info(f"Updated Slack integration for user {user_id}, workspace {workspace_id}")
                return existing

            # Create new integration
            slack_integration = Slack(
                user_id=user_id,
                workspace_id=workspace_id,
                workspace_name=workspace_name,
                bot_token=access_token,
                bot_user_id=bot_user_id,
                slack_user_id=slack_user_id,
                status=status
            )

            db.add(slack_integration)
            await db.commit()
            await db.refresh(slack_integration)

            logger.info(f"Created Slack integration for user {user_id}, workspace {workspace_id}")
            return slack_integration

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error creating Slack integration: {e}")
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, integration_id: int) -> Optional[Slack]:
        """
        Get Slack integration by ID.

        Args:
            db: Database session
            integration_id: Integration ID

        Returns:
            Slack integration or None
        """
        try:
            result = await db.execute(
                select(Slack).where(
                    Slack.id == integration_id,
                    Slack.deleted_at.is_(None)
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Slack integration by ID: {e}")
            return None

    @staticmethod
    async def get_by_user_and_workspace(
        db: AsyncSession,
        user_id: str,
        workspace_id: str
    ) -> Optional[Slack]:
        """
        Get Slack integration by user ID and workspace ID.

        Args:
            db: Database session
            user_id: DRR user ID
            workspace_id: Slack workspace ID

        Returns:
            Slack integration or None
        """
        try:
            result = await db.execute(
                select(Slack).where(
                    Slack.user_id == user_id,
                    Slack.workspace_id == workspace_id,
                    Slack.deleted_at.is_(None)
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Slack integration: {e}")
            return None

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> List[Slack]:
        """
        Get all Slack integrations for a user.

        Args:
            db: Database session
            user_id: DRR user ID

        Returns:
            List of Slack integrations
        """
        try:
            result = await db.execute(
                select(Slack).where(
                    Slack.user_id == user_id,
                    Slack.deleted_at.is_(None)
                ).order_by(Slack.created_at.desc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user Slack integrations: {e}")
            return []

    @staticmethod
    async def update_status(
        db: AsyncSession,
        integration_id: int,
        status: SlackStatus
    ) -> Optional[Slack]:
        """
        Update Slack integration status.

        Args:
            db: Database session
            integration_id: Integration ID
            status: New status

        Returns:
            Updated Slack integration or None
        """
        try:
            # Load ORM entity, update, commit, and return
            result = await db.execute(
                select(Slack).where(Slack.id == integration_id, Slack.deleted_at.is_(None))
            )
            entity = result.scalar_one_or_none()
            if not entity:
                return None
            entity.status = status
            await db.commit()
            await db.refresh(entity)
            logger.info(f"Updated Slack integration {integration_id} status to {status}")
            return entity

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating Slack status: {e}")
            return None

    @staticmethod
    async def delete(db: AsyncSession, integration_id: int) -> bool:
        """
        Soft delete a Slack integration.

        Args:
            db: Database session
            integration_id: Integration ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            from datetime import datetime

            result = await db.execute(
                select(Slack).where(Slack.id == integration_id, Slack.deleted_at.is_(None))
            )
            entity = result.scalar_one_or_none()
            if not entity:
                return False
            entity.deleted_at = datetime.utcnow()
            entity.status = SlackStatus.DISABLED
            await db.commit()
            logger.info(f"Deleted Slack integration {integration_id}")
            return True

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting Slack integration: {e}")
            return False

    @staticmethod
    async def get_active_integrations_by_user(
        db: AsyncSession,
        user_id: str
    ) -> List[Slack]:
        """
        Get all active Slack integrations for a user.

        Args:
            db: Database session
            user_id: DRR user ID

        Returns:
            List of active Slack integrations
        """
        try:
            result = await db.execute(
                select(Slack).where(
                    Slack.user_id == user_id,
                    Slack.status == SlackStatus.ACTIVE,
                    Slack.deleted_at.is_(None)
                ).order_by(Slack.created_at.desc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error getting active Slack integrations: {e}")
            return []


# Global instance
slack_service = SlackService()
