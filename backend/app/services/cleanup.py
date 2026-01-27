"""Background cleanup service for expired verifications and tokens."""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from app.database.database import async_session_maker
from app.models.users import User

logger = logging.getLogger(__name__)


async def cleanup_expired_verifications():
    """
    Clean up expired pending email verifications.

    Sets users with verified=1 (pending) back to verified=0 (unverified)
    if their verification token has expired (24 hours).
    """
    async with async_session_maker() as db:
        try:
            # Find users with pending verification and expired tokens
            result = await db.execute(
                select(User).where(
                    User.verified == 1,  # Pending verification
                    User.reset_token_expires.isnot(None)
                )
            )
            users = result.scalars().all()

            now = datetime.now(timezone.utc)
            expired_count = 0

            for user in users:
                # Check if token has expired
                # Handle both timezone-aware and timezone-naive datetime
                token_expiry = user.reset_token_expires
                if token_expiry:
                    # If token_expiry is naive, assume it's UTC
                    if token_expiry.tzinfo is None:
                        token_expiry = token_expiry.replace(tzinfo=timezone.utc)

                    if token_expiry < now:
                        user.verified = 0  # Reset to unverified
                        user.reset_token = None
                        user.reset_token_expires = None
                        expired_count += 1
                        logger.info(f"Reset expired verification for user: {user.email}")

            if expired_count > 0:
                await db.commit()
                logger.info(f"Cleaned up {expired_count} expired verification(s)")

        except Exception as e:
            logger.error(f"Error in cleanup_expired_verifications: {e}")
            await db.rollback()


async def cleanup_task_loop(interval_seconds: int = 3600):
    """
    Background task that runs cleanup periodically.

    Args:
        interval_seconds: How often to run cleanup (default: 1 hour)
    """
    logger.info(f"Starting cleanup task loop (interval: {interval_seconds}s)")

    while True:
        try:
            await cleanup_expired_verifications()
        except Exception as e:
            logger.error(f"Error in cleanup task loop: {e}")

        # Wait for next interval
        await asyncio.sleep(interval_seconds)
