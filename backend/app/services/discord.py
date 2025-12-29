"""Discord service for database operations."""
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from app.models.discord import Discord, DiscordStatus

logger = logging.getLogger(__name__)


class DiscordService:
    """Service for Discord database operations."""

    @staticmethod
    async def create_discord_integration(
        db: AsyncSession,
        user_id: str,
        discord_user_id: str,
        username: Optional[str],
        global_name: Optional[str],
        guild_id: Optional[str] = None,
        guild_name: Optional[str] = None,
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None,
        status: DiscordStatus = DiscordStatus.ENABLED
    ) -> Discord:
        """Create a new Discord integration (DM or channel)."""
        try:
            # Check if this specific integration already exists (user + guild + channel)
            existing = await DiscordService.get_by_user_guild_channel(
                db, user_id, guild_id, channel_id, include_deleted=True
            )

            if existing:
                # Update existing integration
                existing.username = username
                existing.global_name = global_name
                existing.guild_name = guild_name
                existing.channel_name = channel_name
                existing.status = status
                existing.deleted_at = None

                await db.commit()
                await db.refresh(existing)
                logger.info(f"Updated/reactivated Discord integration for user {user_id}, guild {guild_id}, channel {channel_id}")
                return existing

            # Create new integration
            discord_integration = Discord(
                user_id=user_id,
                discord_user_id=discord_user_id,
                username=username,
                global_name=global_name,
                guild_id=guild_id,
                guild_name=guild_name,
                channel_id=channel_id,
                channel_name=channel_name,
                status=status
            )

            db.add(discord_integration)
            await db.commit()
            await db.refresh(discord_integration)

            logger.info(f"Created Discord integration for user {user_id}, guild {guild_id}, channel {channel_id}")
            return discord_integration

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error creating Discord integration: {e}")
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, integration_id: int) -> Optional[Discord]:
        """Get Discord integration by ID."""
        try:
            result = await db.execute(
                select(Discord).where(
                    Discord.id == integration_id,
                    Discord.deleted_at.is_(None)
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Discord integration by ID: {e}")
            return None

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> List[Discord]:
        """Get all Discord integrations for a user."""
        try:
            result = await db.execute(
                select(Discord).where(
                    Discord.user_id == user_id,
                    Discord.deleted_at.is_(None)
                ).order_by(Discord.created_at.desc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user Discord integrations: {e}")
            return []

    @staticmethod
    async def get_first_by_user(db: AsyncSession, user_id: str) -> Optional[Discord]:
        """Get any existing Discord integration for a user (most recent)."""
        try:
            result = await db.execute(
                select(Discord).where(
                    Discord.user_id == user_id,
                    Discord.deleted_at.is_(None)
                ).order_by(Discord.created_at.desc())
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting first Discord integration: {e}")
            return None

    @staticmethod
    async def update_channel_for_user(
        db: AsyncSession,
        user_id: str,
        channel_id: str,
        guild_id: Optional[str] = None,
    ) -> Optional[Discord]:
        """
        Update the user's Discord integration to point at a server channel.

        Minimal approach: repurpose the existing integration row (DM) to a channel.
        """
        try:
            integ = await DiscordService.get_first_by_user(db, user_id)
            if not integ:
                return None
            integ.guild_id = guild_id
            integ.channel_id = channel_id
            await db.commit()
            await db.refresh(integ)
            logger.info(f"Updated Discord integration {integ.id} to guild={guild_id} channel={channel_id}")
            return integ
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating Discord channel for user: {e}")
            return None

    @staticmethod
    async def get_by_user_and_discord_user(
        db: AsyncSession,
        user_id: str,
        discord_user_id: str,
        include_deleted: bool = False
    ) -> Optional[Discord]:
        """Get Discord integration by user ID and Discord user ID."""
        try:
            query = select(Discord).where(
                Discord.user_id == user_id,
                Discord.discord_user_id == discord_user_id
            )

            if not include_deleted:
                query = query.where(Discord.deleted_at.is_(None))

            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Discord integration: {e}")
            return None

    @staticmethod
    async def update_status(
        db: AsyncSession,
        integration_id: int,
        status: DiscordStatus
    ) -> Optional[Discord]:
        """Update Discord integration status."""
        try:
            result = await db.execute(
                select(Discord).where(Discord.id == integration_id, Discord.deleted_at.is_(None))
            )
            entity = result.scalar_one_or_none()
            if not entity:
                return None
            entity.status = status
            await db.commit()
            await db.refresh(entity)
            logger.info(f"Updated Discord integration {integration_id} status to {status}")
            return entity

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating Discord status: {e}")
            return None

    @staticmethod
    async def delete(db: AsyncSession, integration_id: int) -> bool:
        """Soft delete a Discord integration."""
        try:
            result = await db.execute(
                select(Discord).where(Discord.id == integration_id, Discord.deleted_at.is_(None))
            )
            entity = result.scalar_one_or_none()
            if not entity:
                return False
            entity.deleted_at = datetime.utcnow()
            entity.status = DiscordStatus.DISABLED
            await db.commit()
            logger.info(f"Deleted Discord integration {integration_id}")
            return True

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting Discord integration: {e}")
            return False

    @staticmethod
    async def get_by_user_guild_channel(
        db: AsyncSession,
        user_id: str,
        guild_id: Optional[str],
        channel_id: Optional[str],
        include_deleted: bool = False
    ) -> Optional[Discord]:
        """Get Discord integration by user ID, guild ID, and channel ID."""
        try:
            query = select(Discord).where(
                Discord.user_id == user_id,
                Discord.guild_id == guild_id if guild_id else Discord.guild_id.is_(None),
                Discord.channel_id == channel_id if channel_id else Discord.channel_id.is_(None)
            )

            if not include_deleted:
                query = query.where(Discord.deleted_at.is_(None))

            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting Discord integration by guild/channel: {e}")
            return None

    @staticmethod
    async def create_channel_integration(
        db: AsyncSession,
        base_integration: Discord,
        guild_id: str,
        guild_name: Optional[str],
        channel_id: str,
        channel_name: Optional[str]
    ) -> Discord:
        """
        Create a new channel integration based on an existing DM integration.

        This is used when discovering new channels the bot has access to.
        """
        return await DiscordService.create_discord_integration(
            db=db,
            user_id=base_integration.user_id,
            discord_user_id=base_integration.discord_user_id,
            username=base_integration.username,
            global_name=base_integration.global_name,
            guild_id=guild_id,
            guild_name=guild_name,
            channel_id=channel_id,
            channel_name=channel_name,
            status=DiscordStatus.ENABLED
        )


# Global instance
discord_service = DiscordService()
