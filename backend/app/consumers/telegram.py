"""Telegram Bot API consumer for communicating with Telegram services."""
import os
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class TelegramAPIError(Exception):
    """Custom exception for Telegram API errors."""
    pass


class TelegramConsumer:
    """Telegram Bot API consumer for messaging operations."""

    def __init__(self):
        """Initialize Telegram consumer with bot token."""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot_name = os.getenv("TELEGRAM_BOT_NAME", "@domainrenewalreminder_bot")

        if not self.bot_token:
            logger.warning("Telegram bot token not configured")

        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Telegram chat.

        Args:
            chat_id: Unique identifier for the target chat
            text: Text of the message to be sent
            parse_mode: Mode for parsing entities (HTML, Markdown, or MarkdownV2)
            reply_markup: Additional interface options (inline keyboard, etc.)

        Returns:
            Dict containing the sent message data

        Raises:
            TelegramAPIError: If sending message fails
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }

                if reply_markup:
                    payload["reply_markup"] = reply_markup

                response = await client.post(
                    f"{self.api_base}/sendMessage",
                    json=payload,
                    timeout=10.0
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("description", "Unknown error")
                    logger.error(f"Telegram API error sending message: {error_msg}")
                    raise TelegramAPIError(f"Send message failed: {error_msg}")

                return data.get("result", {})

            except httpx.HTTPError as e:
                logger.error(f"HTTP error sending Telegram message: {e}")
                raise TelegramAPIError(f"HTTP error: {str(e)}")

    async def send_test_message(
        self,
        chat_id: int,
        user_first_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a test message to verify the integration.

        Args:
            chat_id: Chat ID to send test message to
            user_first_name: User's first name for personalization

        Returns:
            Dict containing the sent message data

        Raises:
            TelegramAPIError: If sending test message fails
        """
        greeting = f"Hi {user_first_name}! " if user_first_name else "Hi! "
        text = (
            f"{greeting}🎉\n\n"
            f"<b>DRR Test Connection Successful!</b>\n\n"
            f"Your Telegram integration is working correctly. "
            f"You'll receive domain and SSL expiration notifications here.\n\n"
            f"Domain Renewal Reminder"
        )

        return await self.send_message(chat_id, text, parse_mode="HTML")

    async def leave_chat(self, chat_id: int) -> bool:
        """
        Leave a chat (remove bot from group or channel).

        Args:
            chat_id: Chat ID to leave

        Returns:
            True if successful

        Raises:
            TelegramAPIError: If leaving chat fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base}/leaveChat",
                    json={"chat_id": chat_id},
                    timeout=10.0
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("description", "Unknown error")
                    logger.error(f"Telegram API error leaving chat: {error_msg}")
                    raise TelegramAPIError(f"Leave chat failed: {error_msg}")

                logger.info(f"Bot left chat {chat_id}")
                return True

            except httpx.HTTPError as e:
                logger.error(f"HTTP error leaving Telegram chat: {e}")
                raise TelegramAPIError(f"HTTP error: {str(e)}")

    async def get_chat(self, chat_id: int) -> Dict[str, Any]:
        """
        Get information about a chat.

        Args:
            chat_id: Unique identifier for the target chat

        Returns:
            Dict containing chat information

        Raises:
            TelegramAPIError: If getting chat info fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base}/getChat",
                    json={"chat_id": chat_id},
                    timeout=10.0
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("description", "Unknown error")
                    logger.error(f"Telegram API error getting chat: {error_msg}")
                    raise TelegramAPIError(f"Get chat failed: {error_msg}")

                return data.get("result", {})

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Telegram chat: {e}")
                raise TelegramAPIError(f"HTTP error: {str(e)}")

    async def get_me(self) -> Dict[str, Any]:
        """
        Get information about the bot.

        Returns:
            Dict containing bot information

        Raises:
            TelegramAPIError: If getting bot info fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_base}/getMe",
                    timeout=10.0
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("description", "Unknown error")
                    logger.error(f"Telegram API error getting bot info: {error_msg}")
                    raise TelegramAPIError(f"Get bot info failed: {error_msg}")

                return data.get("result", {})

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Telegram bot info: {e}")
                raise TelegramAPIError(f"HTTP error: {str(e)}")

    async def set_webhook(self, webhook_url: str) -> bool:
        """
        Set the webhook URL for receiving updates.

        Args:
            webhook_url: HTTPS URL to send updates to

        Returns:
            True if webhook was set successfully

        Raises:
            TelegramAPIError: If setting webhook fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base}/setWebhook",
                    json={"url": webhook_url},
                    timeout=10.0
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("description", "Unknown error")
                    logger.error(f"Telegram API error setting webhook: {error_msg}")
                    raise TelegramAPIError(f"Set webhook failed: {error_msg}")

                logger.info(f"Telegram webhook set to: {webhook_url}")
                return True

            except httpx.HTTPError as e:
                logger.error(f"HTTP error setting Telegram webhook: {e}")
                raise TelegramAPIError(f"HTTP error: {str(e)}")

    async def get_webhook_info(self) -> Dict[str, Any]:
        """
        Get current webhook status.

        Returns:
            Dict containing webhook information

        Raises:
            TelegramAPIError: If getting webhook info fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_base}/getWebhookInfo",
                    timeout=10.0
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("description", "Unknown error")
                    logger.error(f"Telegram API error getting webhook info: {error_msg}")
                    raise TelegramAPIError(f"Get webhook info failed: {error_msg}")

                return data.get("result", {})

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Telegram webhook info: {e}")
                raise TelegramAPIError(f"HTTP error: {str(e)}")

    def parse_update(self, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a Telegram webhook update.

        Args:
            update: Update object from Telegram webhook

        Returns:
            Parsed update data or None if not relevant
        """
        # Handle regular message
        if "message" in update:
            message = update["message"]
            return {
                "type": "message",
                "message_id": message.get("message_id"),
                "from": message.get("from"),
                "chat": message.get("chat"),
                "text": message.get("text"),
                "date": message.get("date")
            }

        # Handle bot added/removed to/from group (for bot's own membership changes)
        if "my_chat_member" in update:
            chat_member = update["my_chat_member"]
            new_status = chat_member.get("new_chat_member", {}).get("status")

            # Bot was added to a group
            if new_status in ["member", "administrator"]:
                return {
                    "type": "bot_added_to_chat",
                    "chat": chat_member.get("chat"),
                    "from": chat_member.get("from"),
                    "date": chat_member.get("date")
                }

            # Bot was removed from group
            elif new_status in ["left", "kicked"]:
                return {
                    "type": "bot_removed_from_chat",
                    "chat": chat_member.get("chat"),
                    "from": chat_member.get("from"),
                    "date": chat_member.get("date")
                }

        # Some configurations may send 'chat_member' instead of 'my_chat_member'
        if "chat_member" in update:
            chat_member = update["chat_member"]
            new_status = chat_member.get("new_chat_member", {}).get("status")

            if new_status in ["member", "administrator"]:
                return {
                    "type": "bot_added_to_chat",
                    "chat": chat_member.get("chat"),
                    "from": chat_member.get("from"),
                    "date": chat_member.get("date")
                }
            elif new_status in ["left", "kicked"]:
                return {
                    "type": "bot_removed_from_chat",
                    "chat": chat_member.get("chat"),
                    "from": chat_member.get("from"),
                    "date": chat_member.get("date")
                }

        return None


# Global instance
telegram_consumer = TelegramConsumer()
