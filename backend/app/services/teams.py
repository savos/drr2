"""Teams service for database operations."""
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from app.models.teams import Teams, TeamsStatus

logger = logging.getLogger(__name__)


class TeamsService:
    """Service for Microsoft Teams database operations."""

    @staticmethod
    async def create_teams_integration(
        db: AsyncSession,
        user_id: str,
        teams_user_id: str,
        email: Optional[str],
        username: Optional[str],
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None,
        team_id: Optional[str] = None,
        team_name: Optional[str] = None,
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None,
        status: TeamsStatus = TeamsStatus.ENABLED
    ) -> Teams:
        """Create a new Teams integration (DM or channel)."""
        try:
            # Check if this specific integration already exists (user + team + channel)
            existing = await TeamsService.get_by_user_team_channel(
                db, user_id, team_id, channel_id, include_deleted=True
            )

            if existing:
                # Update existing integration
                existing.email = email
                existing.username = username
                existing.access_token = access_token
                existing.refresh_token = refresh_token
                existing.token_expires_at = token_expires_at
                existing.team_name = team_name
                existing.channel_name = channel_name
                existing.status = status
                existing.deleted_at = None

                await db.commit()
                await db.refresh(existing)
                logger.info(f"Updated/reactivated Teams integration for user {user_id}, team {team_id}, channel {channel_id}")
                return existing

            # Create new integration
            teams_integration = Teams(
                user_id=user_id,
                teams_user_id=teams_user_id,
                email=email,
                username=username,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
                team_id=team_id,
                team_name=team_name,
                channel_id=channel_id,
                channel_name=channel_name,
                status=status
            )

            db.add(teams_integration)
            await db.commit()
            await db.refresh(teams_integration)

            logger.info(f"Created Teams integration for user {user_id}, team {team_id}, channel {channel_id}")
            return teams_integration

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error creating Teams integration: {e}")
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, integration_id: int) -> Optional[Teams]:
        """Get Teams integration by ID."""
        try:
            result = await db.execute(
                select(Teams).where(
                    Teams.id == integration_id,
                    Teams.deleted_at.is_(None)
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Teams integration by ID: {e}")
            return None

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> List[Teams]:
        """Get all Teams integrations for a user."""
        try:
            result = await db.execute(
                select(Teams).where(
                    Teams.user_id == user_id,
                    Teams.deleted_at.is_(None)
                ).order_by(Teams.created_at.desc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user Teams integrations: {e}")
            return []

    @staticmethod
    async def get_first_by_user(db: AsyncSession, user_id: str) -> Optional[Teams]:
        """Get any existing Teams integration for a user (most recent, typically the DM)."""
        try:
            result = await db.execute(
                select(Teams).where(
                    Teams.user_id == user_id,
                    Teams.deleted_at.is_(None)
                ).order_by(Teams.created_at.desc())
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting first Teams integration: {e}")
            return None

    @staticmethod
    async def get_by_user_and_teams_user(
        db: AsyncSession,
        user_id: str,
        teams_user_id: str
    ) -> Optional[Teams]:
        """Get Teams integration by user ID and Teams user ID (for DM lookup)."""
        try:
            result = await db.execute(
                select(Teams).where(
                    Teams.user_id == user_id,
                    Teams.teams_user_id == teams_user_id,
                    Teams.team_id.is_(None),  # DM only (no team)
                    Teams.deleted_at.is_(None)
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Teams integration by user and teams_user: {e}")
            return None

    @staticmethod
    async def get_by_user_team_channel(
        db: AsyncSession,
        user_id: str,
        team_id: Optional[str],
        channel_id: Optional[str],
        include_deleted: bool = False
    ) -> Optional[Teams]:
        """Get Teams integration by user ID, team ID, and channel ID."""
        try:
            query = select(Teams).where(
                Teams.user_id == user_id,
                Teams.team_id == team_id if team_id else Teams.team_id.is_(None),
                Teams.channel_id == channel_id if channel_id else Teams.channel_id.is_(None)
            )

            if not include_deleted:
                query = query.where(Teams.deleted_at.is_(None))

            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Teams integration by user/team/channel: {e}")
            return None

    @staticmethod
    async def create_channel_integration(
        db: AsyncSession,
        base_integration: Teams,
        team_id: str,
        team_name: str,
        channel_id: str,
        channel_name: str
    ) -> Teams:
        """
        Create a new Teams channel integration based on an existing integration (typically DM).
        Uses the same access/refresh tokens from the base integration.
        """
        return await TeamsService.create_teams_integration(
            db=db,
            user_id=base_integration.user_id,
            teams_user_id=base_integration.teams_user_id,
            email=base_integration.email,
            username=base_integration.username,
            access_token=base_integration.access_token,
            refresh_token=base_integration.refresh_token,
            token_expires_at=base_integration.token_expires_at,
            team_id=team_id,
            team_name=team_name,
            channel_id=channel_id,
            channel_name=channel_name,
            status=TeamsStatus.ENABLED
        )

    @staticmethod
    async def update_tokens(
        db: AsyncSession,
        integration_id: int,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None
    ) -> Optional[Teams]:
        """Update access and refresh tokens for a Teams integration."""
        try:
            integration = await TeamsService.get_by_id(db, integration_id)
            if not integration:
                return None

            integration.access_token = access_token
            if refresh_token:
                integration.refresh_token = refresh_token
            if token_expires_at:
                integration.token_expires_at = token_expires_at

            await db.commit()
            await db.refresh(integration)
            logger.info(f"Updated tokens for Teams integration {integration_id}")
            return integration

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating Teams tokens: {e}")
            return None

    @staticmethod
    async def update_status(
        db: AsyncSession,
        integration_id: int,
        status: TeamsStatus
    ) -> Optional[Teams]:
        """Update status of a Teams integration."""
        try:
            integration = await TeamsService.get_by_id(db, integration_id)
            if not integration:
                return None

            integration.status = status
            await db.commit()
            await db.refresh(integration)
            logger.info(f"Updated Teams integration {integration_id} status to {status}")
            return integration

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating Teams status: {e}")
            return None

    @staticmethod
    async def delete(db: AsyncSession, integration_id: int) -> bool:
        """Soft delete a Teams integration."""
        try:
            integration = await TeamsService.get_by_id(db, integration_id)
            if not integration:
                return False

            integration.deleted_at = datetime.utcnow()
            await db.commit()
            logger.info(f"Soft deleted Teams integration {integration_id}")
            return True

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting Teams integration: {e}")
            return False

    @staticmethod
    async def get_all_active(db: AsyncSession) -> List[Teams]:
        """Get all active Teams integrations (for sending notifications)."""
        try:
            result = await db.execute(
                select(Teams).where(
                    Teams.status.in_([TeamsStatus.ENABLED, TeamsStatus.ACTIVE]),
                    Teams.deleted_at.is_(None)
                )
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error getting active Teams integrations: {e}")
            return []
