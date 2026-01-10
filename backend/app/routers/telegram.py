"""Telegram router for webhook integration and messaging."""
import os
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.database import get_db
from app.models.users import User
from app.models.telegram import TelegramStatus, TelegramChatType
from app.schemas.telegram import TelegramRead
from app.utils.security import get_current_user
from app.consumers.telegram import telegram_consumer, TelegramAPIError
from app.services.telegram import telegram_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])


# Request/Response Models
class TestConnectionResponse(BaseModel):
    """Test connection response."""
    success: bool
    message: str


class WebhookInfoResponse(BaseModel):
    """Webhook info response."""
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    last_error_date: int | None = None
    last_error_message: str | None = None


@router.get("/integrations", response_model=List[TelegramRead])
async def get_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all Telegram integrations for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of Telegram integrations
    """
    try:
        integrations = await telegram_service.get_by_user(db, current_user.id)
        logger.info(f"Retrieved {len(integrations)} Telegram integrations for user {current_user.id}")
        return integrations

    except Exception as e:
        logger.error(f"Error retrieving Telegram integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Telegram integrations"
        )


@router.post("/integrations/{integration_id}/test", response_model=TestConnectionResponse)
async def test_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Test a Telegram integration by sending a test message.

    Args:
        integration_id: Integration ID to test
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success status and message
    """
    try:
        # Get integration
        integration = await telegram_service.get_by_id(db, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )

        # Verify ownership
        if integration.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to test this integration"
            )

        # Send test message with validation button
        try:
            # Generate validation token
            import secrets
            validation_token = secrets.token_urlsafe(16)

            # Store validation token temporarily (you could use Redis in production)
            # For now, we'll use a simple approach with the frontend URL
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            validation_url = f"{frontend_url}/dashboard/channels/telegram?verified={validation_token}&integration_id={integration_id}"

            # Create inline keyboard with validation button
            inline_keyboard = {
                "inline_keyboard": [[
                    {
                        "text": "✅ Confirm Connection",
                        "url": validation_url
                    }
                ]]
            }

            # Send test message with button
            greeting = f"Hi {integration.first_name}! " if integration.first_name else "Hi! "
            await telegram_consumer.send_message(
                chat_id=integration.channel_id,
                text=(
                    f"{greeting}🎉\n\n"
                    f"<b>DRR Test Connection</b>\n\n"
                    f"Your Telegram integration is working correctly!\n\n"
                    f"Click the button below to confirm and activate your connection:"
                ),
                parse_mode="HTML",
                reply_markup=inline_keyboard
            )

            # Determine chat type display name
            if integration.chat_type == TelegramChatType.PRIVATE:
                chat_name = "your Telegram DM"
            else:
                chat_name = f"group '{integration.chat_title}'" if integration.chat_title else "the group"

            message = f"Test message sent to {chat_name}. Please click the confirmation button in Telegram."

            logger.info(f"Test message with validation sent to Telegram chat {integration.channel_id}")

            return TestConnectionResponse(
                success=True,
                message=message
            )

        except TelegramAPIError as e:
            logger.error(f"Telegram API error during test: {e}")
            error_msg = str(e)

            # Provide helpful error messages for common issues
            if "Not Found" in error_msg or "chat not found" in error_msg.lower():
                if integration.chat_type == TelegramChatType.PRIVATE:
                    error_msg = (
                        "Cannot send message to this chat. The chat may have been deleted or the bot was blocked. "
                        "Please reconnect by clicking 'Connect Telegram' again and sending /start to the bot."
                    )
                else:
                    error_msg = (
                        "Cannot send message to this group. The bot may have been removed. "
                        "Please add the bot back to the group."
                    )
            elif "Forbidden" in error_msg or "bot was blocked" in error_msg.lower():
                error_msg = (
                    "Bot was blocked by the user. Please unblock the bot in Telegram and try again."
                )

            return TestConnectionResponse(
                success=False,
                message=error_msg
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing Telegram integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test integration"
        )


@router.delete("/integrations/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (soft delete) a Telegram integration.

    Args:
        integration_id: Integration ID to delete
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success status
    """
    try:
        # Get integration
        integration = await telegram_service.get_by_id(db, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )

        # Verify ownership
        if integration.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this integration"
            )

        # For groups, we can remove the bot from the chat
        # For DMs, send a notification message first
        bot_removed = False
        if integration.chat_type == TelegramChatType.PRIVATE:
            # For DMs, send a notification that integration was disconnected
            try:
                await telegram_consumer.send_message(
                    chat_id=integration.channel_id,
                    text=(
                        "👋 <b>Integration Disconnected</b>\n\n"
                        "Your DRR integration has been disconnected from the dashboard. "
                        "You will no longer receive notifications.\n\n"
                        "You can now delete this chat, or send /start to reconnect."
                    ),
                    parse_mode="HTML"
                )
            except TelegramAPIError as e:
                logger.warning(f"Failed to send disconnect notification: {e}")
        else:
            # For groups, leave the chat before deleting
            try:
                await telegram_consumer.leave_chat(integration.channel_id)
                logger.info(f"Bot left group chat {integration.channel_id}")
                bot_removed = True
            except TelegramAPIError as e:
                logger.warning(f"Failed to leave chat {integration.channel_id}: {e}")
                # Continue with deletion even if leaving fails

        # Delete integration
        success = await telegram_service.delete(db, integration_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete integration"
            )

        logger.info(f"Deleted Telegram integration {integration_id}")

        # Return appropriate message based on chat type
        if integration.chat_type == TelegramChatType.PRIVATE:
            message = (
                "Integration disconnected. A notification has been sent to Telegram. "
                "You can now delete the chat or send /start to reconnect."
            )
        elif bot_removed:
            message = "Integration disconnected and bot removed from the group successfully."
        else:
            message = "Integration disconnected. The bot may still be in the group - please remove it manually if needed."

        return {"success": True, "message": message}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Telegram integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete integration"
        )


@router.post("/integrations/{integration_id}/verify")
async def verify_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify and activate a Telegram integration.

    Args:
        integration_id: Integration ID to verify
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success status
    """
    try:
        # Get integration
        integration = await telegram_service.get_by_id(db, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )

        # Verify ownership
        if integration.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to verify this integration"
            )

        # Update status to Active
        from app.models.telegram import TelegramStatus as ModelTelegramStatus
        await telegram_service.update_status(db, integration_id, ModelTelegramStatus.ACTIVE)

        logger.info(f"Verified and activated Telegram integration {integration_id}")

        return {"success": True, "message": "Integration verified and activated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying Telegram integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify integration"
        )


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle incoming Telegram webhook updates.

    This endpoint receives updates from Telegram when:
    - User sends a message to the bot
    - Bot is added to a group
    - Bot is removed from a group

    Args:
        request: FastAPI request object containing webhook payload
        db: Database session

    Returns:
        Success response
    """
    try:
        # Get webhook payload
        update = await request.json()
        try:
            logger.info("Telegram webhook: received update keys=%s", list(update.keys()))
        except Exception:
            logger.exception("Telegram webhook: failed to log update")

        # Parse the update
        parsed = telegram_consumer.parse_update(update)

        if not parsed:
            logger.info("Telegram webhook: update not relevant, ignoring")
            return JSONResponse({"ok": True})

        update_type = parsed.get("type")

        # Handle regular message (user sending /start or any message to bot)
        if update_type == "message":
            logger.info("Telegram webhook: type=message")
            await handle_message(db, parsed)

        # Handle bot added to group
        elif update_type == "bot_added_to_chat":
            logger.info("Telegram webhook: type=bot_added_to_chat chat=%s", parsed.get("chat", {}))
            await handle_bot_added_to_chat(db, parsed)

        # Handle bot removed from group
        elif update_type == "bot_removed_from_chat":
            logger.info("Telegram webhook: type=bot_removed_from_chat chat=%s", parsed.get("chat", {}))
            await handle_bot_removed_from_chat(db, parsed)

        return JSONResponse({"ok": True})

    except Exception as e:
        logger.exception(f"Error handling Telegram webhook: {e}")
        # Return 200 OK even on error to prevent Telegram from retrying
        return JSONResponse({"ok": True})


@router.post("/webhook/set")
async def set_telegram_webhook():
    """Convenience endpoint to set Telegram webhook to the public URL."""
    public_base = os.getenv("FRONTEND_URL")
    if not public_base:
        raise HTTPException(status_code=500, detail="FRONTEND_URL not configured")
    webhook_url = public_base.rstrip("/") + "/api/telegram/webhook"
    try:
        ok = await telegram_consumer.set_webhook(webhook_url)
        if ok:
            return {"ok": True, "webhook_url": webhook_url}
        raise HTTPException(status_code=500, detail="Failed to set Telegram webhook")
    except TelegramAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


async def handle_message(db: AsyncSession, parsed: Dict[str, Any]):
    """
    Handle incoming message from user.

    Creates or updates a DM integration when user sends /start command.

    Args:
        db: Database session
        parsed: Parsed message data
    """
    try:
        message_text = parsed.get("text", "")
        chat = parsed.get("chat", {})
        from_user = parsed.get("from", {})

        chat_id = chat.get("id")
        chat_type = chat.get("type")
        user_id = from_user.get("id")

        # Only handle private messages (DMs)
        if chat_type != "private":
            return

        # Handle /stop command
        if message_text.startswith("/stop"):
            logger.info(f"Received /stop command from user {user_id} (chat {chat_id})")
            await handle_stop_command(db, chat_id, user_id)
            return

        # Check if /start command
        if not message_text.startswith("/start"):
            return

        logger.info(f"Received /start command from user {user_id}")

        # Extract DRR user ID from /start command
        # Format: /start user_<drr_user_id>
        parts = message_text.split("_")
        if len(parts) < 2:
            # Send help message
            await telegram_consumer.send_message(
                chat_id=chat_id,
                text=(
                    "👋 Welcome to DRR (Domain Renewal Reminder)!\n\n"
                    "To connect your Telegram account, please use the link from the DRR dashboard.\n\n"
                    "Go to: Dashboard → Channels → Telegram"
                )
            )
            return

        drr_user_id = parts[1]

        # Create or update integration
        from app.models.telegram import TelegramStatus as ModelTelegramStatus
        integration = await telegram_service.create_telegram_integration(
            db=db,
            user_id=drr_user_id,
            telegram_user_id=user_id,
            channel_id=chat_id,
            chat_type=TelegramChatType.PRIVATE,
            chat_title=None,
            username=from_user.get("username"),
            first_name=from_user.get("first_name"),
            last_name=from_user.get("last_name"),
            language_code=from_user.get("language_code"),
            status=ModelTelegramStatus.ENABLED
        )

        # Send confirmation message
        await telegram_consumer.send_message(
            chat_id=chat_id,
            text=(
                f"✅ <b>Connected Successfully!</b>\n\n"
                f"Your Telegram is now connected to DRR. "
                f"You'll receive domain and SSL expiration notifications here.\n\n"
                f"You can test the connection from the DRR dashboard."
            ),
            parse_mode="HTML"
        )

        logger.info(f"Created Telegram DM integration for user {drr_user_id}")

    except Exception as e:
        logger.exception(f"Error handling Telegram message: {e}")


async def handle_bot_added_to_chat(db: AsyncSession, parsed: Dict[str, Any]):
    """
    Handle bot being added to a group.

    Creates a group integration when bot is added to a group.

    Args:
        db: Database session
        parsed: Parsed update data
    """
    try:
        chat = parsed.get("chat", {})
        from_user = parsed.get("from", {})

        chat_id = chat.get("id")
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        user_id = from_user.get("id")

        # Only handle groups/supergroups/channels
        if chat_type not in ["group", "supergroup", "channel"]:
            return

        logger.info(f"Bot added to {chat_type} {chat_id} by user {user_id}")

        # Try to attribute this group to a DRR user that already connected via DM
        drr_user_id = await telegram_service.get_user_id_by_telegram_user(db, user_id)

        if drr_user_id:
            # Create or update a group integration for this user
            from app.schemas.telegram import TelegramStatus
            await telegram_service.create_telegram_integration(
                db=db,
                user_id=drr_user_id,
                telegram_user_id=None,  # group doesn't map to a single tg user
                channel_id=chat_id,
                chat_type=TelegramChatType(chat_type),
                chat_title=chat_title,
                username=None,
                first_name=None,
                last_name=None,
                language_code=None,
                status=TelegramStatus.ENABLED,
            )

            await telegram_consumer.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ This group is now connected to DRR.\n\n"
                    f"The owner can manage settings in the DRR dashboard."
                )
            )
        else:
            # Fall back to instructive message if we cannot resolve the owner yet
            await telegram_consumer.send_message(
                chat_id=chat_id,
                text=(
                    f"👋 Hi! I'm the DRR (Domain Renewal Reminder) bot.\n\n"
                    f"To receive notifications in this group, the person who added me needs to:\n"
                    f"1. Send me a /start message in a private chat\n"
                    f"2. Connect their DRR account from the dashboard\n\n"
                    f"Then I'll automatically be able to send notifications here!"
                )
            )

    except Exception as e:
        logger.error(f"Error handling bot added to chat: {e}")


async def handle_bot_removed_from_chat(db: AsyncSession, parsed: Dict[str, Any]):
    """
    Handle bot being removed from a group.

    Soft deletes the group integration when bot is removed.

    Args:
        db: Database session
        parsed: Parsed update data
    """
    try:
        chat = parsed.get("chat", {})
        chat_id = chat.get("id")

        logger.info(f"Bot removed from chat {chat_id}")

        # Find integration by channel_id and soft delete it
        # We don't know the user_id, so we need to query differently
        from sqlalchemy import select
        from app.models.telegram import Telegram

        result = await db.execute(
            select(Telegram).where(
                Telegram.channel_id == chat_id,
                Telegram.deleted_at.is_(None)
            )
        )
        integration = result.scalar_one_or_none()

        if integration:
            await telegram_service.delete(db, integration.id)
            logger.info(f"Deleted Telegram integration for chat {chat_id}")

    except Exception as e:
        logger.error(f"Error handling bot removed from chat: {e}")


async def handle_stop_command(db: AsyncSession, chat_id: int, telegram_user_id: int):
    """
    Handle /stop command from user.

    Soft deletes the DM integration and sends a goodbye message.

    Args:
        db: Database session
        chat_id: Telegram chat ID
        telegram_user_id: Telegram user ID
    """
    try:
        # Find integration by channel_id (chat_id for DMs)
        from sqlalchemy import select
        from app.models.telegram import Telegram

        result = await db.execute(
            select(Telegram).where(
                Telegram.channel_id == chat_id,
                Telegram.chat_type == TelegramChatType.PRIVATE,
                Telegram.deleted_at.is_(None)
            )
        )
        integration = result.scalar_one_or_none()

        if integration:
            # Soft delete the integration
            await telegram_service.delete(db, integration.id)
            logger.info(f"Stopped Telegram integration for chat {chat_id}")

            # Send goodbye message
            await telegram_consumer.send_message(
                chat_id=chat_id,
                text=(
                    "👋 <b>Notifications Stopped</b>\n\n"
                    "Your DRR integration has been disconnected. You will no longer receive notifications.\n\n"
                    "To reconnect, visit the DRR dashboard and click 'Connect Telegram' again.\n\n"
                    "You can now delete this chat if you'd like."
                ),
                parse_mode="HTML"
            )
        else:
            # No active integration found
            await telegram_consumer.send_message(
                chat_id=chat_id,
                text=(
                    "ℹ️ You don't have an active DRR integration.\n\n"
                    "To connect, visit the DRR dashboard and click 'Connect Telegram'."
                )
            )

    except Exception as e:
        logger.error(f"Error handling /stop command: {e}")


@router.get("/webhook/info", response_model=WebhookInfoResponse)
async def get_webhook_info():
    """
    Get current Telegram webhook information.

    Returns:
        Webhook status and configuration
    """
    try:
        webhook_info = await telegram_consumer.get_webhook_info()

        return WebhookInfoResponse(
            url=webhook_info.get("url", ""),
            has_custom_certificate=webhook_info.get("has_custom_certificate", False),
            pending_update_count=webhook_info.get("pending_update_count", 0),
            last_error_date=webhook_info.get("last_error_date"),
            last_error_message=webhook_info.get("last_error_message")
        )

    except TelegramAPIError as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/bot/info")
async def get_bot_info():
    """
    Get Telegram bot information.

    Returns:
        Bot username, name, and other details
    """
    try:
        bot_info = await telegram_consumer.get_me()
        return bot_info

    except TelegramAPIError as e:
        logger.error(f"Error getting bot info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/start/link")
async def get_start_link(
    current_user: User = Depends(get_current_user)
):
    """
    Get the Telegram /start link for connecting the user's account.

    Args:
        current_user: Current authenticated user

    Returns:
        Telegram deep link URL
    """
    bot_name = telegram_consumer.bot_name.lstrip("@")
    start_link = f"https://t.me/{bot_name}?start=user_{current_user.id}"

    return {
        "start_link": start_link,
        "bot_name": telegram_consumer.bot_name
    }
def _verify_telegram_secret(request: Request, expected: str) -> bool:
    token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    return bool(expected) and token == expected


@router.post("/webhook")
async def telegram_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Telegram webhook endpoint with secret token verification.
    Configure your bot's webhook with the same secret token.
    """
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not secret:
        return JSONResponse(status_code=500, content={"error": "TELEGRAM_WEBHOOK_SECRET not configured"})
    if not _verify_telegram_secret(request, secret):
        return JSONResponse(status_code=401, content={"error": "Invalid secret"})

    try:
        update = await request.json()
    except Exception:
        update = {}

    # Minimal scaffold: acknowledge; extend to handle messages/joins if needed
    logger.info("Telegram webhook received update type=%s", update.get("message", {}).get("chat", {}).get("type") if update else None)
    return JSONResponse(content={"ok": True})
